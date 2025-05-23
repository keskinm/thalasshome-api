import json
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy
from testcontainers.postgres import PostgresContainer

from dashboard import create_app
from dashboard.constants import APP_DIR, DB_DIR
from dashboard.container import container
from dashboard.db.test_client import TestDBClient
from dashboard.lib.services import parse_order


@pytest.fixture()
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
def test_db_client(postgres_container):
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
            conn.execute(sqlalchemy.text(sql))

    test_client = TestDBClient(engine)
    container.register_singleton("DB_CLIENT", test_client, force=True)
    return test_client


@pytest.fixture(autouse=True)
def db_transaction(test_db_client):
    """Rollback all changes after each test."""
    test_db_client.begin()
    yield
    test_db_client.rollback()


#  ------------------------------------ FUNCTION SCOPED ------------------------------


@pytest.fixture(scope="function")
def sample_order_line_item(test_db_client):
    file_path = APP_DIR / "utils" / "orders" / "samples" / "2025_discounted.json"
    with open(file_path, "r", encoding="utf-8") as f:
        order = json.load(f)
    parsed_order, line_items = parse_order(order)
    line_items[0]["from_date"] = (
        datetime.now(timezone.utc).date() + timedelta(days=5)
    ).isoformat()
    line_items[0]["to_date"] = (
        datetime.now(timezone.utc).date() + timedelta(days=6)
    ).isoformat()
    test_db_client.insert_into_table("orders", parsed_order)
    test_db_client.insert_into_table("line_items", line_items)
    yield (parsed_order, line_items)
    test_db_client.delete_from_table("line_items", {"order_id": parsed_order["id"]})
    test_db_client.delete_from_table("orders", {"id": parsed_order["id"]})


@pytest.fixture
def sample_provider(test_db_client):
    _user = test_db_client.select_from_table(
        "users",
        "*",
        conditions=None,
        limit=1,
        single=True,
    )
    yield _user


@pytest.fixture
def sample_order():
    return {
        "id": 5555123486903,
        "created_at": "2025-03-02T14:23:40+01:00",
        "email": "sign.pls.up@gmail.com",
        "phone": "None",
        "total_price": "16.00",
        "updated_at": "2025-03-02T14:23:42+01:00",
        "shipping_address": {
            "first_name": "Sasha",
            "address1": "7 Rue du Stade Albert Baud",
            "phone": "0700000000",
            "city": "Annemasse",
            "zip": "74100",
            "province": "None",
            "country": "France",
            "last_name": "Keskin",
            "address2": "None",
            "company": "None",
            "latitude": 46.190304,
            "longitude": 6.242890999999999,
            "name": "Sasha Keskin",
            "country_code": "FR",
            "province_code": "None",
        },
        "shipping_lat": 46.190304,
        "shipping_lon": 6.242890999999999,
        "shipping_phone": "0700000000",
    }


@pytest.fixture
def sample_line_items():
    return [
        {
            "id": 14137901646007,
            "product": "jacuzzi4p",
            "price": 64.0,
            "from_date": "2025-03-03",
            "to_date": "2025-03-05",
            "quantity": 1,
            "order_id": 5555123486903,
        }
    ]


#  ------------------------------------------------------------------------------------
