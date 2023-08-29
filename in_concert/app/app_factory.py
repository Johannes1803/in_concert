from typing import Annotated

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, FastAPI
from jwt.jwks_client import PyJWKClient
from starlette.middleware.sessions import SessionMiddleware

from in_concert.dependencies.auth.token_validation import (
    HTTPBearerWithCookie,
    JwkTokenVerifier,
)
from in_concert.dependencies.auth.user_authorization import UserAuthorizerJWT
from in_concert.routers import auth_router
from in_concert.settings import Auth0Settings


def create_app(auth0_settings: Auth0Settings):
    app = FastAPI()

    app.add_middleware(SessionMiddleware, secret_key=auth0_settings.middleware_secret_key)

    oauth = OAuth()
    authentication_router = auth_router.create_router(auth0_settings, oauth)
    app.include_router(authentication_router)

    jwks_url = f"https://{auth0_settings.domain}/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    token_verifier = JwkTokenVerifier(settings=auth0_settings, jwks_client=jwks_client, decoder=jwt.decode)

    http_bearer = HTTPBearerWithCookie()

    user_authorizer = UserAuthorizerJWT(token_verifier=token_verifier, bearer=http_bearer)

    @app.get("/")
    async def read_main():
        return {"message": "Hello World"}

    @app.get("/private")
    async def read_private(is_authenticated: Annotated[dict, Depends(user_authorizer.is_authenticated_current_user)]):
        return {"secret": "secret123"}

    return app
