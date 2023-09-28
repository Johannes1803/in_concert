from typing import Annotated

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, FastAPI
from jwt.jwks_client import PyJWKClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.sessions import SessionMiddleware

from in_concert.app.models import Base, User
from in_concert.app.schemas import UserSchema
from in_concert.dependencies.auth.token_validation import (
    HTTPBearerWithCookie,
    JwkTokenVerifier,
)
from in_concert.dependencies.auth.user_authorization import (
    UserAuthorizerJWT,
    UserOAuth2Integrator,
)
from in_concert.routers import auth_router
from in_concert.settings import Auth0Settings


def get_db_session_factory(settings_auth) -> sessionmaker:
    engine = create_engine(settings_auth.db_connection_string.get_secret_value())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    return SessionLocal


def create_app(auth0_settings: Auth0Settings, session_factory: sessionmaker):
    app = FastAPI()

    app.add_middleware(SessionMiddleware, secret_key=auth0_settings.middleware_secret_key)

    def get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    http_bearer = HTTPBearerWithCookie()

    jwks_url = f"https://{auth0_settings.domain}/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    token_verifier = JwkTokenVerifier(settings=auth0_settings, jwks_client=jwks_client, decoder=jwt.decode)

    user_authorizer = UserAuthorizerJWT(token_verifier=token_verifier, bearer=http_bearer)
    user_oauth_integrator = UserOAuth2Integrator(user_authorizer, user_model=User)

    oauth = OAuth()
    authentication_router = auth_router.create_router(auth0_settings, oauth, user_oauth_integrator)
    app.include_router(authentication_router)

    @app.get("/")
    async def read_main():
        return {"message": "Hello World"}

    @app.get("/private")
    async def read_private(is_authenticated: Annotated[dict, Depends(user_authorizer.is_authenticated_current_user)]):
        return {"secret": "secret123"}

    @app.post("/users", status_code=201)
    async def create_user(
        user_schema: UserSchema,
        db_session: Annotated[Session, Depends(get_session)],
    ):
        user = User(**user_schema.model_dump())
        user_id: int = user.insert(db_session)
        return {"id": user_id}

    return app
