import pytest
from flask import Flask

from dashboard import create_app
from dashboard.db.client import supabase_cli


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_supabase(mocker):
    return mocker.patch("dashboard.db.client.supabase_cli", autospec=True)
