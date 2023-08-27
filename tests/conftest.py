import pytest

from in_concert.settings import Auth0Settings, Auth0SettingsTest


@pytest.fixture
def settings_auth() -> Auth0Settings:
    test_settings_auth = Auth0SettingsTest()
    return test_settings_auth
