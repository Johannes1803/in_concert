from typing import Any

import jwt
import sqlalchemy
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import DeclarativeBase, Session

from in_concert.dependencies.auth.token_validation import (
    HTTPBearerWithCookie,
    JwkTokenVerifier,
)


class Base(DeclarativeBase):
    pass


class UserAuthorizerJWT:
    """
    Manage the authorization of the current user based on authorization with JWT tokens in oauth2 model.
    """

    def __init__(self, token_verifier: JwkTokenVerifier, bearer: HTTPBearerWithCookie) -> None:
        self.token_verifier = token_verifier
        self.bearer = bearer
        super().__init__()

    async def is_authenticated_current_user(self, request: Request) -> bool:
        """
        Determine whether current user is authenticated for specified scope.

        :param request: starlette request object
        :return: true if authenticated, false otherwise
        """
        return await self._is_authorized_current_user(request, scope="")

    async def _is_authorized_current_user(self, request: Request, scope: str = "") -> bool:
        """
        Determine whether current user is authorized for specified scope.

        :param request: starlette request object
        :param scope: scope to grant access to
        :return: true if authorized, false otherwise
        """
        payload = await self._get_payload(request, scope)
        return True if payload else False

    async def get_current_user_id(self, request: Request) -> str:
        """Get the current user's id from the payload."""
        payload = await self._get_payload(request)
        try:
            return payload["sub"]
        except KeyError:
            raise HTTPException(status_code=401, detail="Invalid bearer token")

    async def _get_payload(self, request: Request, scope: str = "") -> dict:
        """
        Get payload from token.

        :param request: starlette request object
        :param scope: scope to grant access to
        :return: payload
        """
        http_credentials: HTTPAuthorizationCredentials = await self.bearer(request)
        token: str = http_credentials.credentials
        try:
            payload = self.token_verifier.verify(token)
        except jwt.PyJWTError as exc_info:
            raise HTTPException(status_code=401, detail=f"{exc_info}")
        else:
            return payload

    async def set_session(self, token: dict, request: Request) -> None:
        """Set the current session for the current user."""
        self.bearer.set_token(token, request)


class UserOAuth2Integrator:
    """Integrate the UserAuthorizer with the internal user model."""

    def __init__(
        self,
        user_authorizer: UserAuthorizerJWT,
        user_model: Base,
    ) -> None:
        """Init the UserOAUth2Integrator.

        :param user_authorizer: integrates authorization with oauth2 model
        :param user_model: orm class of internal sql user model
        """
        self.user_model = user_model
        self.user_authorizer = user_authorizer

    async def get_current_user(self, request: Request, db_session: Session) -> Any:
        """Get the current user from the database.

        :param request: starlette request object
        :param db_session: sqlalchemy session
        :return: user model
        """
        current_user_id: str = self.user_authorizer.get_current_user_id(request)

        with db_session:
            user_from_db = db_session.get(self.user_model, current_user_id)
        if not user_from_db:
            raise KeyError("Current user not found in database.")
        else:
            return user_from_db

    async def add_current_user(self, request, db_session: Session) -> str:
        """Add the user as represented by oauth2 jwt token to the database.

        :param request: starlette request object
        :param db_session: sqlalchemy session
        :return: user id
        """
        user_id: str = self.user_authorizer.get_current_user_id(request)
        user = self.user_model(id=user_id)
        user_id = user.insert(db_session)
        return user_id

    async def sync_current_user(self, request, db_session: Session):
        """Sync the internal user_model db with oauth2 token.

        :param request: starlette request object
        :param db_session: sqlalchemy session object
        """
        try:
            _ = await self.add_current_user(request, db_session)
        except sqlalchemy.exc.IntegrityError:
            pass
