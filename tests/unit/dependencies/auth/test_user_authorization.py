from unittest import mock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError

from in_concert.app.models import User
from in_concert.dependencies.auth.user_authorization import (
    Base,
    UserAuthorizerJWT,
    UserOAUth2Integrator,
)


class TestUserAuthorizerJWT:
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
    def setup(self, db_session) -> Base:
        user = User(id="auth0|1")
        with db_session:
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
        return user

    @pytest.fixture
    def user_authorizer(
        self,
    ) -> UserAuthorizerJWT:
        user_authorizer = mock.MagicMock()
        user_authorizer.get_current_user_id.return_value = "auth0|1"
        return user_authorizer

    @pytest.fixture
    def user_authorizer_with_db_entry(self, user_authorizer, setup) -> UserAuthorizerJWT:
        return user_authorizer

    @pytest.mark.asyncio
    async def test_get_user_should_return_user_if_logged_in_and_in_db(
        self, user_authorizer_with_db_entry, request_obj, db_session
    ):
        user_integrator = UserOAUth2Integrator(user_authorizer_with_db_entry, User)
        user = await user_integrator.get_current_user(request=request_obj, db_session=db_session)
        assert user
        assert user.id == "auth0|1"

    @pytest.mark.asyncio
    async def test_get_user_should_raise_key_error_if_not_in_db(self, user_authorizer, request_obj, db_session):
        user_integrator = UserOAUth2Integrator(user_authorizer, User)
        with pytest.raises(KeyError):
            _ = await user_integrator.get_current_user(request=request_obj, db_session=db_session)

    @pytest.mark.asyncio
    async def test_add_user_should_add_new_user_to_db(self, user_authorizer, request_obj, db_session):
        user_integrator = UserOAUth2Integrator(user_authorizer, User)
        with db_session:
            assert db_session.get(User, "auth0|1") is None
            _ = await user_integrator.add_current_user(request=request_obj, db_session=db_session)
            user = db_session.get(User, "auth0|1")
            assert user
            assert user.id == "auth0|1"

    @pytest.mark.asyncio
    async def test_add_existing_user_should_raise_error(self, user_authorizer_with_db_entry, request_obj, db_session):
        user_integrator = UserOAUth2Integrator(user_authorizer_with_db_entry, User)
        with pytest.raises(IntegrityError):
            _ = await user_integrator.add_current_user(request=request_obj, db_session=db_session)

    @pytest.mark.asyncio
    async def test_sync_current_user_should_add_new_user_to_db(self, user_authorizer, request_obj, db_session):
        user_integrator = UserOAUth2Integrator(user_authorizer, User)
        with db_session:
            assert db_session.get(User, "auth0|1") is None
            _ = await user_integrator.sync_current_user(request=request_obj, db_session=db_session)
            user = db_session.get(User, "auth0|1")
            assert user
            assert user.id == "auth0|1"

    @pytest.mark.asyncio
    async def test_sync_current_user_should_have_no_effect_existing_user(
        self, user_authorizer_with_db_entry, request_obj, db_session
    ):
        user_integrator = UserOAUth2Integrator(user_authorizer_with_db_entry, User)
        with db_session:
            assert db_session.get(User, "auth0|1")
            _ = await user_integrator.sync_current_user(request=request_obj, db_session=db_session)
            user = db_session.get(User, "auth0|1")
            assert user
            assert user.id == "auth0|1"
