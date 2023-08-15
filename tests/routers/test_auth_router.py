from unittest import mock

import pytest
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import Response
from fastapi.testclient import TestClient

from in_concert.routers.auth_router import create_router
from in_concert.settings import test_settings_auth


class TestAuthRouter:
    @pytest.fixture
    def request_object(self):
        request_obj = mock.MagicMock()
        request_obj.url_for = mock.MagicMock(return_value="/callback")

    @pytest.fixture
    def oauth(self):
        oauth = OAuth()
        oauth.auth0 = mock.AsyncMock()
        oauth.auth0.authorize_redirect = mock.AsyncMock(return_value=Response(status_code=302))
        oauth.auth0.authorize_access_token = mock.AsyncMock(return_value={"access_token": "valid_token"})
        oauth.register = mock.MagicMock()
        return oauth

    @pytest.fixture
    def client(self, oauth):
        router = create_router(test_settings_auth, oauth=oauth)
        return TestClient(router)

    @pytest.mark.asyncio
    def test_login(self, client):
        response = client.get("/login")
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_callback_sets_token_as_cookie(self, client, oauth):
        response = client.get("/callback", allow_redirects=False)

        oauth.auth0.authorize_access_token.assert_called_once()
        assert response.status_code == 307

        assert response.cookies["access_token"] == '"Bearer valid_token"'
