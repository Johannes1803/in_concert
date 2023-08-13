from unittest import mock

import pytest
from fastapi import HTTPException

from in_concert.authorization import HTTPBearerWithCookie, JwkTokenVerifier


class TestHTTPBearerWithCookie:
    @pytest.fixture
    def request_obj(self):
        request = mock.MagicMock()
        request.cookies = {"access_token": "bearer valid_jwt_token"}
        return request

    @pytest.fixture
    def request_obj_no_token(self):
        request = mock.MagicMock()
        request.cookies = {}
        return request

    @pytest.fixture
    def request_obj_malformed_token(self):
        request = mock.MagicMock()
        request.cookies = {"acces_token": "not_bearer jwt pattern"}
        return request

    @pytest.mark.asyncio
    async def test_get_token_from_cookie_should_return_token_if_set(self, request_obj):
        bearer = HTTPBearerWithCookie()
        http_credentials = await bearer(request_obj)
        assert http_credentials

    @pytest.mark.asyncio
    async def test_get_token_should_raise_401_if_cookie_not_set(self, request_obj_no_token):
        bearer = HTTPBearerWithCookie()
        with pytest.raises(HTTPException) as e:
            _ = await bearer(request_obj_no_token)
            assert e.status_code == 401

    @pytest.mark.asyncio
    async def test_get_token_should_raise_401_if_token_not_expected_format(self, request_obj_no_token):
        bearer = HTTPBearerWithCookie()
        with pytest.raises(HTTPException) as e:
            _ = await bearer(request_obj_no_token)
            assert e.status_code == 401


class TestJwkTokenVerifier:
    @pytest.fixture
    def settings(self):
        return mock.MagicMock()

    @pytest.fixture
    def jwks_client(self):
        jwks_client = mock.MagicMock()
        jwks_client.get_signing_key_from_jwt.return_value = mock.MagicMock(return_value=mock.MagicMock(key="valid_key"))
        return jwks_client

    @pytest.fixture
    def decoder(self):
        return mock.MagicMock(return_value={"payload": "valid_payload"})

    def test_valid_token_should_return_payload(self, settings, jwks_client, decoder):
        token_verifier = JwkTokenVerifier(settings, jwks_client, decoder=decoder)

        payload = token_verifier.verify("valid_token")
        jwks_client.get_signing_key_from_jwt.assert_called_once_with("valid_token")

        decoder.assert_called_once()
        assert payload == {"payload": "valid_payload"}
