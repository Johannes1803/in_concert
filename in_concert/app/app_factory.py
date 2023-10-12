from typing import Annotated, Any

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jwt.jwks_client import PyJWKClient
from sqlalchemy import engine
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_404_NOT_FOUND
from starlette_wtf import StarletteForm

from definitions import PROJECT_ROOT
from in_concert.app.forms import VenueForm
from in_concert.app.models import Base, User, Venue, VenueManager, delete_db_entry
from in_concert.app.schemas import UserSchema, VenueManagerSchema, VenueSchema
from in_concert.dependencies.auth.token_validation import (
    HTTPBearerWithCookie,
    JwkTokenVerifier,
)
from in_concert.dependencies.auth.user_authorization import (
    UserAuthorizerJWT,
    UserOAuth2Integrator,
)
from in_concert.dependencies.db_session import DBSessionDependency
from in_concert.routers.auth import auth_router
from in_concert.settings import Auth0Settings


def create_app(auth0_settings: Auth0Settings, engine: engine):
    app = FastAPI()

    # configure auth
    app.add_middleware(SessionMiddleware, secret_key=auth0_settings.middleware_secret_key)
    http_bearer = HTTPBearerWithCookie()
    jwks_url = f"https://{auth0_settings.domain}/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    token_verifier = JwkTokenVerifier(settings=auth0_settings, jwks_client=jwks_client, decoder=jwt.decode)

    user_authorizer = UserAuthorizerJWT(token_verifier=token_verifier, bearer=http_bearer)
    user_oauth_integrator = UserOAuth2Integrator(user_authorizer, user_model=User)
    oauth = OAuth()

    # setup db engine
    db_session_dep = DBSessionDependency(engine)

    # add auth router
    authentication_router = auth_router.create_router(
        auth0_settings, oauth, user_oauth_integrator, db_session_dep=db_session_dep
    )
    app.include_router(authentication_router)

    # setup internal sql dbs
    Base.metadata.create_all(engine)

    # setup templates
    templates = Jinja2Templates(directory=PROJECT_ROOT / "in_concert/app/templates")

    # mount static files
    app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "in_concert/app/static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def read_main(request: Request):
        return templates.TemplateResponse("home.html", {"request": request})

    @app.get("/private")
    async def read_private(is_authenticated: Annotated[bool, Security(user_authorizer.is_authenticated_current_user)]):
        return {"secret": "secret123"}

    @app.post("/users", status_code=201)
    async def create_user(
        user_schema: UserSchema,
        db_session: Annotated[Any, Depends(db_session_dep)],
        request: Request,
    ):
        user = User(**user_schema.model_dump())
        user_id: int = user.insert(db_session)
        return {"id": user_id}

    @app.post("/venue_managers", status_code=201)
    async def create_venue_manager(
        venue_manager_Schema: VenueManagerSchema,
        db_session: Annotated[Any, Depends(db_session_dep)],
        request: Request,
    ):
        venue_manager = VenueManager(**venue_manager_Schema.model_dump())
        venue_manager_id: int = venue_manager.insert(db_session)
        return {"id": venue_manager_id}

    @app.api_route(
        "/venues",
        methods=["GET", "POST"],
        dependencies=[
            Security(user_oauth_integrator.user_authorizer.is_authorized_current_user, scopes=("create:venues",)),
        ],
    )
    async def create_venue(
        db_session: Annotated[Any, Depends(db_session_dep)],
        request: Request,
        response: Response,
    ):
        venue_form: StarletteForm = await VenueForm.from_formdata(request)
        if await venue_form.validate_on_submit():
            venue_schema = VenueSchema(**venue_form.data)
            venue = Venue(**venue_schema.model_dump())
            venue_id: int = venue.insert(db_session)
            response.status_code = 201
            return {"id": venue_id}

        html = templates.TemplateResponse("venue_form.html", {"form": venue_form, "request": request})
        return html

    @app.delete("/venues/{venue_id:int}")
    def delete_venue(
        venue_id: int,
        db_session: Annotated[Any, Depends(db_session_dep)],
    ):
        try:
            venue_id = delete_db_entry(db_session, venue_id, Venue)
        except KeyError as e:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
        return {"id": venue_id}

    return app
