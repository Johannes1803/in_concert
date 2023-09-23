from typing import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from in_concert.app.models import Base
from in_concert.settings import Auth0Settings, Auth0SettingsTest
from tests.setup import get_bearer_token


@pytest.fixture
def settings_auth() -> Auth0Settings:
    test_settings_auth = Auth0SettingsTest()
    return test_settings_auth


@pytest.fixture()
def bearer_token(settings_auth) -> dict:
    return get_bearer_token(settings_auth)


@pytest.fixture
def db_session(settings_auth) -> Iterator[Engine]:
    engine = create_engine(settings_auth.db_connection_string.get_secret_value())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    yield SessionLocal()
    Base.metadata.drop_all(engine)
