from unittest import mock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from in_concert.dependencies.auth.user_authorization import UserAuthorizerJWT


class TestUserAuthorizerJWT:
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
    def token_verifier(self):
        token_verifier = mock.MagicMock()
        token_verifier.verify.return_value = {"sub": "auth0|1234567890"}
        return token_verifier

    @pytest.fixture
    def token_verifier_decode_error(self):
        token_verifier = mock.MagicMock()
        token_verifier.verify.side_effect = jwt.DecodeError("Invalid token")
        return token_verifier

    @pytest.fixture
    def token_verifier_missing_id_key(self):
        token_verifier = mock.MagicMock()
        token_verifier.verify.return_value = {"not_id": "123"}
        return token_verifier

    @pytest.mark.asyncio
    async def test_is_authorized_current_user_should_return_true_if_valid_jwt_token(
        self, token_verifier, bearer, request_obj
    ):
        user_authorizer = UserAuthorizerJWT(token_verifier, bearer)
        is_authorized = await user_authorizer.is_authenticated_current_user(request_obj)
        assert is_authorized

        assert await bearer.called_once()
        assert token_verifier.verify.called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_is_authorized_current_user_should_raise_401_if_malformatted_jwt_token(
        self, token_verifier, bearer_invalid, request_obj
    ):
        user_authorizer = UserAuthorizerJWT(token_verifier, bearer_invalid)
        with pytest.raises(HTTPException) as excinfo:
            _ = await user_authorizer.is_authenticated_current_user(request_obj)
            assert excinfo.status_code == 401

        assert await bearer_invalid.called_once()

    @pytest.mark.asyncio
    async def test_is_authorized_current_user_should_raise_401_if_decode_error(
        self, token_verifier_decode_error, bearer, request_obj
    ):
        user_authorizer = UserAuthorizerJWT(token_verifier_decode_error, bearer)
        with pytest.raises(HTTPException) as excinfo:
            _ = await user_authorizer.is_authenticated_current_user(request_obj)
            assert excinfo.status_code == 401

        assert await bearer.called_once()
        assert token_verifier_decode_error.verify.called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_get_current_user_id_should_return_user_id_if_logged_in(self, token_verifier, bearer, request_obj):
        user_authorizer = UserAuthorizerJWT(token_verifier, bearer)
        user_id = await user_authorizer.get_current_user_id(request_obj)
        assert user_id == "auth0|1234567890"

    @pytest.mark.asyncio
    async def test_get_current_user_id_should_raise_500_if_unexpeted_token_format(
        self, token_verifier_missing_id_key, bearer, request_obj
    ):
        user_authorizer = UserAuthorizerJWT(token_verifier_missing_id_key, bearer)
        with pytest.raises(HTTPException) as excinfo:
            _ = await user_authorizer.get_current_user_id(request_obj)
            assert excinfo.status_code == 401


class TestUserOAUth2Integrator:
    @pytest.fixture
    def user_authorizer(self):
        user_authorizer = mock.MagicMock()
        user_authorizer.get_current_user_id.return_value = "auth0|1"
        return user_authorizer

    @pytest.fixture
    def user_model(self):
        pass
