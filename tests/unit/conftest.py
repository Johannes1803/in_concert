from typing import Iterator
from unittest import mock

import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from in_concert.app.app_factory import create_app
from in_concert.app.models import Base
from in_concert.dependencies.db_session import DBSessionDependency
from in_concert.settings import Auth0Settings, Auth0SettingsTest
from tests.setup import get_bearer_token


@pytest.fixture
def settings_auth() -> Auth0Settings:
    test_settings_auth = Auth0SettingsTest()
    return test_settings_auth


@pytest.fixture()
def bearer_token(settings_auth) -> dict:
    return get_bearer_token(settings_auth)


@pytest.fixture()
def engine(settings_auth) -> Iterator[create_engine]:
    engine = create_engine(settings_auth.db_connection_string.get_secret_value())
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
def client(settings_auth, engine):
    app = create_app(settings_auth, engine=engine)
    return TestClient(app)
