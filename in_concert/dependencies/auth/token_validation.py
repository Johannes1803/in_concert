from typing import Callable, Optional

import jwt
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED

from in_concert.dependencies.schemas import OauthTokenSchema


class HTTPBearerWithCookie(HTTPBearer):
    """Credential setter/getter for bearer token in cookie."""

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        """
        Get the access token from cookies.

        :param request: The request to get the token from
        :return: jwt bearer token
        :raises HTTPException: If the token is not set or format is invalid
        """
        authorization: Optional[str] = request.cookies.get("access_token")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

    def set_token(self, token_dict: dict, response: Response) -> None:
        """Set the access token in the cookie.

        :param token: oauth2 access token
        :param response: _description_
        """
        response.set_cookie(
            key="access_token",
            value=f'Bearer {token_dict.get("access_token")}',
            httponly=True,
            samesite="strict",
            secure=True,
        )


class RequestLikeTokenDict:
    """Adapter class for the token dict to look like a request w.r.t the interface relevant for the bearer."""

    def __init__(self, token_dict: dict):
        self.oauth_token = OauthTokenSchema(**token_dict)
        self.cookies: dict = {}
        self.cookies["access_token"] = f"{self.oauth_token.token_type} {self.oauth_token.access_token}"


class JwkTokenVerifier:
    """Does all the token verification using PyJWT"""

    def __init__(self, settings, jwks_client: jwt.PyJWKClient, decoder: Callable = jwt.decode):
        self.settings = settings
        self.jwks_client = jwks_client
        self.decoder = decoder

    def verify(self, access_token: str) -> dict:
        """
        Verifies the token and returns the payload if successful.

        param: token: The access token to verify
        return: dict: The payload if successful
        raises: jwt.exceptions.DecodeError if decoding the signing key or the token fails
        raises: jwt.exceptions.InvalidSignatureError if the signature is invalid
        raises: jwt.exceptions.ExpiredSignatureError if the token is expired
        """
        signing_key = self.jwks_client.get_signing_key_from_jwt(access_token).key
        payload = self.decoder(
            access_token,
            signing_key,
            algorithms=self.settings.algorithms,
            audience=self.settings.audience,
            issuer=self.settings.issuer,
        )
        return payload
