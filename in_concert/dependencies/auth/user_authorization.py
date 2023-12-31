import abc
from typing import Any

import jwt
import openfga_sdk
import sqlalchemy
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes
from openfga_sdk.client.client import OpenFgaClient
from openfga_sdk.client.models import (
    ClientCheckRequest,
    ClientTuple,
    ClientWriteRequest,
)
from sqlalchemy.orm import Session

from in_concert.dependencies.auth.token_validation import (
    HTTPBearerWithCookie,
    JwkTokenVerifier,
)


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
        Determine whether current user is authenticated.

        :param request: starlette request object
        :return: true if authenticated
        """
        empty_security_scope: SecurityScopes = SecurityScopes()
        return await self._is_authorized_current_user(request, scopes=empty_security_scope)

    async def is_authorized_current_user(self, request: Request, scopes: SecurityScopes) -> bool:
        """Determine whether current user is authorized for specified scope.

        :param request: starlette request object
        :param scope: scopes to grant access to
        :return: true if authorized
        """
        return await self._is_authorized_current_user(request, scopes=scopes)

    async def _is_authorized_current_user(self, request: Request, scopes: SecurityScopes) -> bool:
        """
        Determine whether current user is authorized for specified scope.

        :param request: starlette request object
        :param scopes: scopes to grant access to
        :return: true if authorized
        """

        payload = await self._get_payload(request)

        if scopes.scopes:
            try:
                granted_permissions = payload["permissions"]
            except KeyError:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            else:
                for scope in scopes.scopes:
                    if scope not in granted_permissions:
                        raise HTTPException(status_code=403, detail="Insufficient permissions")
                return True
        else:
            return True

    async def get_current_user_id(self, request: Request) -> str:
        """Get the current user's id from the payload."""
        payload = await self._get_payload(request)
        try:
            return payload["sub"]
        except KeyError:
            raise HTTPException(status_code=401, detail="Invalid bearer token")

    async def _get_payload(self, request: Request) -> dict:
        """
        Get payload from access token.

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

    def set_session(self, token_dict: dict, response: Response) -> None:
        """Set the current session for the current user.

        :param token_dict: oauth2 access token"""
        self.bearer.set_token(token_dict, response)


class UserAuthorizerFGA:
    """
    Manage the authorization of the current user based on FGA authorization model.
    """

    def __init__(
        self, fga_configuration: openfga_sdk.ClientConfiguration, user_authorizer_jwt: UserAuthorizerJWT
    ) -> None:
        self.fga_configuration = fga_configuration
        self.user_authorizer_jwt = user_authorizer_jwt

    async def is_authorized_current_user(self, request: Request, scopes: SecurityScopes, object_id: int) -> bool:
        """Determine whether current user is authorized for fga scope.

        :param request: starlette request object
        :param scope: scope to grant access to
        :return: true if authorized
        """
        response = await self._check_authorization_current_user(request, scopes, object_id)
        if not response.allowed:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return True

    async def _check_authorization_current_user(
        self, request: Request, scopes: SecurityScopes, object_id: int
    ) -> Response:
        user_id: str = await self.user_authorizer_jwt.get_current_user_id(request)
        user_str: str = f"user:{user_id}"

        relation_object_type: list = scopes.scopes[0].split(":")
        relation = relation_object_type[0]
        object_type = relation_object_type[1]
        object_str = f"{object_type}:{object_id}"

        options = {"store_id": self.fga_configuration.store_id}
        body = ClientCheckRequest(
            user=user_str,
            relation=relation,
            object=object_str,
        )
        async with OpenFgaClient(self.fga_configuration) as fga_client:
            # Enter a context with an instance of the OpenFgaClient
            response = await fga_client.check(body, options)
            await fga_client.close()
        return response

    async def add_permissions(self, request: Request, relations: list[str], object_type: str, object_id: int) -> None:
        """Add permissions for a user to an object.

        :param relation: relation of user to object
        :param object_type: type of object
        :param object_id: id of object
        :param permissions: permissions to add to object
        """
        user_id: str = await self.user_authorizer_jwt.get_current_user_id(request)
        user_str: str = f"user:{user_id}"
        object_str = f"{object_type}:{object_id}"

        options = {"store_id": self.fga_configuration.store_id}
        for relation in relations:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user=user_str,
                        relation=relation,
                        object=object_str,
                    ),
                ],
            )
            async with OpenFgaClient(self.fga_configuration) as fga_client:
                # Enter a context with an instance of the OpenFgaClient
                await fga_client.write(body, options)
                await fga_client.close()
        return

    async def remove_permissions(
        self, request: Request, object_type: str, object_id: int, relations: list[str]
    ) -> None:
        """Remove permissions for user w.r.t. specified object.

        :param object_type: type of object
        :param object_id: id of object
        :param relations: relations to remove from object
        """
        user_id: str = await self.user_authorizer_jwt.get_current_user_id(request)
        user: str = f"user:{user_id}"
        object_: str = f"{object_type}:{object_id}"

        options = {"store_id": self.fga_configuration.store_id}
        for relation in relations:
            body = ClientWriteRequest(
                deletes=[
                    ClientTuple(
                        user=user,
                        relation=relation,
                        object=object_,
                    ),
                ],
            )
            async with OpenFgaClient(self.fga_configuration) as fga_client:
                # Enter a context with an instance of the OpenFgaClient
                await fga_client.write(body, options)
                await fga_client.close()
        return


class UserABC(abc.ABC):
    @abc.abstractmethod
    def __init__(self, id: int) -> None:
        pass

    @abc.abstractmethod
    def insert(request: Request, db_session: Session) -> int:
        pass


class UserOAuth2Integrator:
    """Integrate the UserAuthorizer with the internal user model."""

    def __init__(
        self,
        user_authorizer: UserAuthorizerJWT,
        user_model: UserABC,
        user_authorizer_fga: UserAuthorizerFGA,
    ) -> None:
        """Init the UserOAUth2Integrator.

        :param user_authorizer: integrates authorization with oauth2 model
        :param user_model: orm class of internal sql user model
        """
        self.user_model = user_model
        self.user_authorizer = user_authorizer
        self.user_authorizer_fga = user_authorizer_fga

    async def get_current_user(self, request: Request, db_session: Session) -> Any:
        """Get the current user from the database.

        :param request: starlette request object
        :param db_session: sqlalchemy session
        :return: user model
        """
        current_user_id: str = await self.user_authorizer.get_current_user_id(request)

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
        user_id: str = await self.user_authorizer.get_current_user_id(request)
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
            return
        return
