from unittest import mock

import pytest
from fastapi import HTTPException

from in_concert.authorization import HTTPBearerWithCookie


@pytest.fixture
def request_obj():
    request = mock.MagicMock()
    request.cookies = {"access_token": "bearer valid_jwt_token"}
    return request


@pytest.fixture
def request_obj_no_token():
    request = mock.MagicMock()
    request.cookies = {}
    return request


@pytest.fixture
def request_obj_malformed_token():
    request = mock.MagicMock()
    request.cookies = {"acces_token": "not_bearer jwt pattern"}
    return request


@pytest.mark.asyncio
async def test_get_token_from_cookie_should_return_token_if_set(request_obj):
    bearer = HTTPBearerWithCookie()
    http_credentials = await bearer(request_obj)
    assert http_credentials


@pytest.mark.asyncio
async def test_get_token_should_raise_401_if_cookie_not_set(request_obj_no_token):
    bearer = HTTPBearerWithCookie()
    with pytest.raises(HTTPException) as e:
        _ = await bearer(request_obj_no_token)
        assert e.status_code == 401


@pytest.mark.asyncio
async def test_get_token_should_raise_401_if_token_not_expected_format(request_obj_no_token):
    bearer = HTTPBearerWithCookie()
    with pytest.raises(HTTPException) as e:
        _ = await bearer(request_obj_no_token)
        assert e.status_code == 401
