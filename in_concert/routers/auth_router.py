from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.routing import APIRouter

from in_concert.settings import Auth0Settings


def create_router(auth_settings: Auth0Settings, oauth: OAuth):
    router = APIRouter()

    CONF_URL = f"https://{auth_settings.domain}/.well-known/openid-configuration"
    oauth.register(
        name="auth0",
        server_metadata_url=CONF_URL,
        client_id=auth_settings.client_id,
        client_secret=auth_settings.client_secret,
        audience=auth_settings.audience,
    )

    @router.get("/login")
    async def login(request: Request):
        redirect_uri = request.url_for("auth")
        return await oauth.auth0.authorize_redirect(request, redirect_uri)

    @router.get("/auth")
    async def auth(request: Request):
        pass

    return router
