from typing import Iterator
from unittest import mock

import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from in_concert.app.app_factory import AppFactory
from in_concert.app.models import Base
from in_concert.dependencies.db_session import DBSessionDependency
from in_concert.settings import AppSettings, AppSettingsTest
from tests.setup import get_bearer_token


@pytest.fixture
def app_settings_test() -> AppSettings:
    app_settings_test = AppSettingsTest()
    return app_settings_test


@pytest.fixture()
def bearer_token(app_settings_test) -> dict:
    return get_bearer_token(app_settings_test)


@pytest.fixture()
def engine(app_settings_test) -> Iterator[create_engine]:
    engine = create_engine(app_settings_test.db_connection_string.get_secret_value())
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session_factory(engine) -> Iterator[sessionmaker]:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    yield SessionLocal
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_session_factory) -> Session:
    session = db_session_factory()
    yield session
    session.close()


@pytest.fixture
def db_session_dep(engine) -> DBSessionDependency:
    db_session_dep = DBSessionDependency(engine=engine)
    yield db_session_dep


@pytest.fixture
def request_obj():
    return mock.MagicMock()


@pytest.fixture
def response_obj(self):
    return Response()


@pytest.fixture
def client(app_settings_test, engine):
    app_factory = AppFactory()
    app_factory.configure(app_settings_test)
    app = app_factory.create_app(app_settings_test, engine=engine)
    return TestClient(app)


@pytest.fixture
def client_no_auth_checks(app_settings_test, engine):
    """A test client where all security dependencies are overridden or mocked."""
    app_factory = AppFactory()
    app_factory.configure(app_settings_test)
    app_factory.user_oauth_integrator.user_authorizer_fga.add_permissions = mock.AsyncMock(return_value=True)
    app_factory.user_oauth_integrator.user_authorizer_fga.remove_permissions = mock.AsyncMock()
    app = app_factory.create_app(app_settings_test, engine=engine, override_security_dependencies=True)
    return TestClient(app)
