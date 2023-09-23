from behave import fixture
from fastapi.testclient import TestClient

from in_concert.app.app_factory import create_app, get_db_session_factory
from in_concert.settings import Auth0Settings, Auth0SettingsTest


@fixture
def settings_auth(context) -> Auth0Settings:
    test_settings_auth = Auth0SettingsTest()
    context.settings_auth = test_settings_auth
    return context.settings_auth


@fixture
def session_factory(context):
    context.session_factory = get_db_session_factory(context.settings_auth)
    return context.session_factory


@fixture
def test_client(context):
    app = create_app(context.settings_auth, context.session_factory)
    test_client = TestClient(app)
    context.test_client = test_client
    return context.test_client
