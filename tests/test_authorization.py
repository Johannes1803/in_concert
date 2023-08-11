from unittest import mock

import pytest

from in_concert.authorization import HTTPBearerWithCookie


@pytest.fixture
def request_obj():
    request = mock.MagicMock()
    request.cookies = {"access_token": "bearer valid_jwt_token"}
    return request


@pytest.mark.asyncio
async def test_get_token_from_cookie_should_return_token_if_set(request_obj):
    bearer = HTTPBearerWithCookie()
    http_credentials = await bearer(request_obj)
    assert http_credentials
