import pytest

from in_concert.settings import Auth0Settings, Auth0SettingsTest
from tests.setup import get_bearer_token


@pytest.fixture
def settings_auth() -> Auth0Settings:
    test_settings_auth = Auth0SettingsTest()
    return test_settings_auth


@pytest.fixture()
def bearer_token(settings_auth) -> dict:
    return get_bearer_token(settings_auth)
