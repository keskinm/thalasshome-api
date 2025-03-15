import json
import os

import pytest
import sqlalchemy
from testcontainers.postgres import PostgresContainer

from dashboard import create_app
from dashboard.constants import APP_DIR, DB_DIR
from dashboard.db.client_wrapper import DB_CLIENT
from dashboard.lib.services import parse_order


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    return app.test_client()


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
    DB_CLIENT.test_db_engine = engine
    return engine


#  ------------------------------------ FUNCTION SCOPED ------------------------------


@pytest.fixture(scope="function")
def insert_random_order_with_line_item_sample(db_engine):
    file_path = APP_DIR / "utils" / "orders" / "samples" / "2025_discounted.json"
    with open(file_path, "r", encoding="utf-8") as f:
        order = json.load(f)
    parsed_order, line_items = parse_order(order)
    DB_CLIENT.insert_into_table("orders", parsed_order, db_engine=db_engine)
    DB_CLIENT.insert_into_table("line_items", line_items, db_engine=db_engine)


#  ------------------------------------------------------------------------------------
