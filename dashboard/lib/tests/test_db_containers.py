# test_db_testcontainers.py
import os

import pytest
import sqlalchemy
from testcontainers.postgres import PostgresContainer

from dashboard.constants import DB_DIR
from dashboard.db.client import call_rpc, select_from_table


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


def test_select_order(db_engine):
    result = select_from_table(
        "orders",
        select_columns="*",
        conditions={"email": "neuneu@gmail.com"},
        limit=1,
        single=True,
        db_engine=db_engine,
    )
    assert result is not None
