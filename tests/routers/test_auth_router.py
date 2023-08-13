from unittest import mock

import pytest
from authlib.integrations.starlette_client import OAuth
from fastapi.testclient import TestClient

from in_concert.routers.auth_router import create_router
from in_concert.settings import Auth0SettingsTest


class TestAuthRouter:
    @pytest.fixture
    def oauth(self):
        oauth = OAuth()
        oauth.auth0 = mock.MagicMock()
        oauth.auth0.authorize_redirect = mock.MagicMock()

    @pytest.fixture
    def client(self, oauth):
        router = create_router(Auth0SettingsTest, oauth=oauth)
        return TestClient(router)

    def test_login(self, client):
        response = client.get("/login")
        assert response.status_code == 302
