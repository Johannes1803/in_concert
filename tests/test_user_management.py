from unittest import mock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from in_concert.user_management import UserManagerJWT


class TestUserManagerJWT:
    @pytest.fixture
    def request_obj(self):
        return mock.MagicMock()

    @pytest.fixture
    def bearer(self):
        async_mock = mock.AsyncMock(
            return_value=HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        )
        return async_mock

    @pytest.fixture
    def bearer_invalid(self):
        async_mock = mock.AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid bearer token"))
        return async_mock

    @pytest.fixture
    def oauth(self):
        return mock.MagicMock()

    @pytest.fixture
    def token_verifier(self):
        token_verifier = mock.MagicMock()
        token_verifier.verify.return_value = {"payload": "valid_payload"}
        return token_verifier

    @pytest.mark.asyncio
    async def test_is_authorized_current_user_should_return_true_if_valid_jwt_token(
        self, token_verifier, bearer, oauth, request_obj
    ):
        user_manager = UserManagerJWT(token_verifier, bearer, oauth)
        is_authorized = await user_manager.is_authorized_current_user(request_obj)
        assert is_authorized

        assert bearer.called_once()
        assert token_verifier.verify.called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_is_authorized_current_user_should_raise_401_if_malformatted_jwt_token(
        self, token_verifier, bearer_invalid, oauth, request_obj
    ):
        user_manager = UserManagerJWT(token_verifier, bearer_invalid, oauth)
        with pytest.raises(HTTPException) as excinfo:
            _ = await user_manager.is_authorized_current_user(request_obj)
            assert excinfo.status_code == 401

        assert bearer_invalid.called_once()
