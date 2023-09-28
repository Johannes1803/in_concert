from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter

from in_concert.dependencies.auth.user_authorization import UserOAuth2Integrator
from in_concert.settings import Auth0Settings


def create_router(auth_settings: Auth0Settings, oauth: OAuth, user_oauth_integrator: UserOAuth2Integrator) -> APIRouter:
    router = APIRouter()

    CONF_URL = f"https://{auth_settings.domain}/.well-known/openid-configuration"
    oauth.register(
        name="auth0",
        server_metadata_url=CONF_URL,
        client_id=auth_settings.client_id,
        client_secret=auth_settings.client_secret,
        audience=auth_settings.audience,
    )

    @router.get("/login", response_class=RedirectResponse)
    async def login(request: Request) -> RedirectResponse:
        redirect_uri = request.url_for("auth")
        return await oauth.auth0.authorize_redirect(request, redirect_uri)

    @router.get("/callback", response_class=RedirectResponse)
    async def auth(
        request: Request,
    ) -> RedirectResponse:
        token = await oauth.auth0.authorize_access_token(request)

        response = RedirectResponse(url="/")
        user_oauth_integrator.user_authorizer.set_session(token=token, response=response)

        user_oauth_integrator.sync_current_user(request=request)
        return response

    return router
