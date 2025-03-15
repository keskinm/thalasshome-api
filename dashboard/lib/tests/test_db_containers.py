# test_db_testcontainers.py
import pytest
import sqlalchemy
from testcontainers.postgres import PostgresContainer

from dashboard.constants import DB_DIR


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgis/postgis:13-3.1") as postgres:
        yield postgres


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
