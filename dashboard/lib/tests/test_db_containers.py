# test_db_testcontainers.py
import json
import os

import pytest
import sqlalchemy
from testcontainers.postgres import PostgresContainer

from dashboard.constants import APP_DIR, DB_DIR
from dashboard.db.client import call_rpc, insert_into_table, select_from_table
from dashboard.lib.services import parse_order


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgis/postgis:15-3.3") as postgres:
        yield postgres


@pytest.fixture(autouse=True, scope="session")
def set_testing_env():
    """Used in custom db client wrapper."""
    os.environ["TESTING"] = "true"


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    engine = sqlalchemy.create_engine(postgres_container.get_connection_url())
    for sql_filepath_suffix in [
        "create/users.sql",
        "create/orders.sql",
        "create/locations.sql",
        "create/insert_initial_data.sql",
        "functions.sql",
    ]:
        with open(DB_DIR / sql_filepath_suffix, "r") as f:
            sql = f.read()
        with engine.begin() as conn:
            conn.execute(sql)
    return engine


#  ------------------------------------ FUNCTION SCOPED ------------------------------


@pytest.fixture(scope="function")
def insert_random_order_with_line_item_sample(db_engine):
    file_path = APP_DIR / "utils" / "orders" / "samples" / "2025_discounted.json"
    with open(file_path, "r", encoding="utf-8") as f:
        order = json.load(f)
    parsed_order, line_items = parse_order(order)
    insert_into_table("orders", parsed_order, db_engine=db_engine)
    insert_into_table("line_items", line_items, db_engine=db_engine)


#  ------------------------------------------------------------------------------------


def test_example(db_engine):
    with db_engine.connect() as conn:
        result = conn.execute("SELECT COUNT(*) FROM users;")
        count = result.scalar()
        assert count >= 4


def test_rpc(db_engine):
    result = call_rpc(
        "check_delivery_men_around_point",
        {"in_shipping_lon": 4.31, "in_shipping_lat": 45.39},
        db_engine=db_engine,
    )
    assert result is not None


def test_select_order(db_engine, insert_random_order_with_line_item_sample):
    result = select_from_table(
        "orders",
        select_columns="*",
        conditions={"email": "sign.pls.up@gmail.com"},
        limit=1,
        single=True,
        db_engine=db_engine,
    )
    assert result is not None
