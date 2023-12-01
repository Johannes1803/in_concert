from behave import fixture
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from in_concert.app.app_factory import create_app
from in_concert.settings import AppSettingsTest, Auth0Settings


@fixture
def settings_auth(context) -> Auth0Settings:
    test_settings_auth = AppSettingsTest()
    context.settings_auth = test_settings_auth
    return context.settings_auth


@fixture
def engine(context):
    context.engine = create_engine(context.settings_auth.db_connection_string.get_secret_value())
    return context.engine


@fixture
def test_client(context):
    app = create_app(context.settings_auth, context.engine)
    test_client = TestClient(app)
    context.test_client = test_client
    return context.test_client
