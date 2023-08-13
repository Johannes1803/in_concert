from abc import ABC, abstractmethod

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.security import HTTPBearer

from in_concert.authorization import JwkTokenVerifier


class UserManager(ABC):
    """
    Manage the current user.
    """

    @abstractmethod
    async def is_authorized_current_user(self, request: Request, scope: str = "") -> bool:
        """
        Implement this method to determine if current user is authorized for specified scope.

        :param request: starlette request object
        :param scope: scope to grant access to
        :return: true if authorized, false otherwise
        """
        pass


class UserManagerJWT(UserManager):
    """
    Manage the current user based on authorization with JWT tokens in oauth2 model.
    """

    def __init__(self, token_verifier: JwkTokenVerifier, bearer: HTTPBearer, oauth: OAuth) -> None:
        self.token_verifier = token_verifier
        self.bearer = bearer
        self.oauth = oauth
        super().__init__()

    async def is_authorized_current_user(self, request: Request, scope: str = "") -> bool:
        """
        Implement this method to determine if current user is authorized for specified scope.

        :param request: starlette request object
        :param scope: scope to grant access to
        :return: true if authorized, false otherwise
        """
        pass
