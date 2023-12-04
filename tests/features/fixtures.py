from behave import fixture
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from in_concert.app.app_factory import AppFactory
from in_concert.settings import AppSettings, AppSettingsTest


@fixture
def app_settings_test(context) -> AppSettings:
    app_settings_test = AppSettingsTest()
    context.app_settings_test = app_settings_test
    return context.app_settings_test


@fixture
def engine(context):
    context.engine = create_engine(context.app_settings_test.db_connection_string.get_secret_value())
    return context.engine


@fixture
def test_client(context):
    app_factory = AppFactory()
    app_factory.configure(context.app_settings_test)
    app = app_factory.create_app(app_settings=context.app_settings_test, engine=context.engine)
    test_client = TestClient(app)
    context.test_client = test_client
    return context.test_client
