from unittest import mock

import pytest
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import Response
from fastapi.testclient import TestClient

from in_concert.dependencies.auth.user_authorization import UserOAuth2Integrator
from in_concert.routers.auth.auth_router import create_router


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
    def user_oauth_integrator(self):
        user_oauth_integrator: UserOAuth2Integrator = mock.MagicMock()
        user_oauth_integrator.sync_current_user = mock.AsyncMock(return_value=None)
        user_oauth_integrator.user_authorizer = mock.MagicMock()
        user_oauth_integrator.user_authorizer.set_session = mock.AsyncMock(return_value="1")
        return user_oauth_integrator

    @pytest.fixture
    def client(self, oauth, settings_auth, user_oauth_integrator, db_session_dep):
        router = create_router(
            settings_auth, oauth=oauth, user_oauth_integrator=user_oauth_integrator, db_session_dep=db_session_dep
        )
        return TestClient(router)

    def test_login(self, client):
        response = client.get("/login")
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_callback_sets_session(self, client, oauth, user_oauth_integrator):
        response = client.get("/callback", follow_redirects=False)

        oauth.auth0.authorize_access_token.assert_called_once()
        assert response.status_code == 307

        user_oauth_integrator.user_authorizer.set_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_callback_syncs_user(self, client, user_oauth_integrator):
        client.get("/callback", follow_redirects=False)

        user_oauth_integrator.sync_current_user.assert_called_once()
