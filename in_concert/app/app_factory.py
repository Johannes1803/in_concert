import asyncio
from typing import Annotated, Any

import jwt
import openfga_sdk
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
from in_concert.app.forms import BandForm, VenueForm
from in_concert.app.models import Band, Base, User, Venue, delete_db_entry
from in_concert.app.schemas import BandSchema, UserSchema, VenueSchema
from in_concert.dependencies.auth.token_validation import (
    HTTPBearerWithCookie,
    JwkTokenVerifier,
)
from in_concert.dependencies.auth.user_authorization import (
    UserAuthorizerFGA,
    UserAuthorizerJWT,
    UserOAuth2Integrator,
)
from in_concert.dependencies.db_session import DBSessionDependency
from in_concert.routers.auth import auth_router
from in_concert.settings import AppSettings


class AppFactory:
    def __init__(self) -> None:
        self.user_authorizer_jwt: UserAuthorizerJWT = None
        self.user_authorizer_fga: UserAuthorizerFGA = None
        self.user_oauth_integrator: UserOAuth2Integrator = None
        self.app = None

    def configure(self, app_settings: AppSettings):
        self.configure_user_authorizer_jwt(app_settings)
        self.configure_user_authorizer_fga(app_settings)
        self.configure_user_oauth_integrator()

    def configure_user_authorizer_jwt(self, app_settings: AppSettings):
        http_bearer = HTTPBearerWithCookie()
        jwks_url = f"https://{app_settings.domain}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        token_verifier = JwkTokenVerifier(settings=app_settings, jwks_client=jwks_client, decoder=jwt.decode)
        self.user_authorizer_jwt = UserAuthorizerJWT(token_verifier=token_verifier, bearer=http_bearer)

    def configure_user_authorizer_fga(self, app_settings: AppSettings):
        assert self.user_authorizer_jwt
        # configure fga auth
        credentials = openfga_sdk.credentials.Credentials(
            method="client_credentials",
            configuration=openfga_sdk.credentials.CredentialConfiguration(
                api_issuer=app_settings.fga_api_token_issuer,
                api_audience=app_settings.fga_api_audience,
                client_id=app_settings.fga_client_id,
                client_secret=app_settings.fga_client_secret,
            ),
        )
        fga_configuration = openfga_sdk.client.ClientConfiguration(
            api_scheme=app_settings.fga_api_scheme,
            api_host=app_settings.fga_api_host,
            store_id=app_settings.fga_store_id,
            # authorization_model_id=app_settings.fga_model_id,
            credentials=credentials,  # Credentials are not needed if connecting to the Playground API
        )
        self.user_authorizer_fga = UserAuthorizerFGA(fga_configuration, self.user_authorizer_jwt)

    def configure_user_oauth_integrator(self):
        assert self.user_authorizer_jwt
        assert self.user_authorizer_fga
        self.user_oauth_integrator = UserOAuth2Integrator(
            self.user_authorizer_jwt, user_model=User, user_authorizer_fga=self.user_authorizer_fga
        )

    def create_app(
        self, app_settings: AppSettings, engine: engine, override_security_dependencies: bool = False
    ) -> FastAPI:
        app = FastAPI()
        app.user_oauth_integrator = self.user_oauth_integrator

        # configure jwt auth
        app.add_middleware(SessionMiddleware, secret_key=app_settings.middleware_secret_key)
        oauth = OAuth()

        # setup db engine
        db_session_dep = DBSessionDependency(engine)

        # add auth router
        authentication_router = auth_router.create_router(
            app_settings, oauth, self.user_oauth_integrator, db_session_dep=db_session_dep
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

        @app.get(
            "/private",
            dependencies=[
                Security(
                    self.user_oauth_integrator.user_authorizer.is_authorized_current_user, scopes=("create:venues",)
                ),
            ],
        )
        async def read_private():
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

        @app.api_route(
            "/venues",
            methods=["GET", "POST"],
            dependencies=[
                Security(
                    self.user_oauth_integrator.user_authorizer.is_authorized_current_user, scopes=("create:venues",)
                ),
            ],
        )
        async def create_venue(
            db_session: Annotated[Any, Depends(db_session_dep)],
            user_id: Annotated[str, Depends(self.user_oauth_integrator.user_authorizer.get_current_user_id)],
            request: Request,
            response: Response,
        ):
            venue_form: StarletteForm = await VenueForm.from_formdata(request)
            if await venue_form.validate_on_submit():
                venue_form_dict = venue_form.data.copy()
                venue_form_dict["manager_id"] = user_id
                venue_schema = VenueSchema(**venue_form_dict)
                venue = Venue(**venue_schema.model_dump())
                venue_id: int = venue.insert(db_session)
                response.status_code = 201

                await self.user_oauth_integrator.user_authorizer_fga.add_permissions(
                    request, ["can_delete", "can_update"], "venue", venue_id
                )

                return {"id": venue_id}

            html = templates.TemplateResponse("venue_form.html", {"form": venue_form, "request": request})
            return html

        @app.delete(
            "/venues/{object_id:int}",
            dependencies=[
                Security(
                    self.user_oauth_integrator.user_authorizer.is_authorized_current_user, scopes=("delete:venues",)
                ),
                Security(
                    self.user_oauth_integrator.user_authorizer_fga.is_authorized_current_user,
                    scopes=("can_delete:venue",),
                ),
            ],
        )
        async def delete_venue(
            object_id: int,
            db_session: Annotated[Any, Depends(db_session_dep)],
            request: Request,
        ):
            try:
                venue_id = delete_db_entry(db_session, object_id, Venue)
            except KeyError as e:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
            else:
                await self.user_oauth_integrator.user_authorizer_fga.remove_permissions(
                    request=request, object_type="venue", object_id=venue_id, relations=["can_delete", "can_update"]
                )
                return {"id": venue_id}

        @app.get("/list_venues")
        def list_venues(
            db_session: Annotated[Any, Depends(db_session_dep)],
            request: Request,
        ):
            venues = db_session.query(Venue).all()
            html = templates.TemplateResponse("venues.html", {"venues": venues, "request": request})
            return html

        @app.get("/venues/{object_id:int}")
        def get_venue(
            object_id: int,
            db_session: Annotated[Any, Depends(db_session_dep)],
            request: Request,
        ):
            venue = db_session.get(Venue, object_id)
            if not venue:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Venue not found")
            html = templates.TemplateResponse("venue.html", {"venue": venue, "request": request})
            return html

        @app.api_route(
            "/bands",
            methods=["GET", "POST"],
            dependencies=[
                Security(
                    self.user_oauth_integrator.user_authorizer.is_authorized_current_user, scopes=("create:bands",)
                ),
            ],
        )
        async def create_band(
            db_session: Annotated[Any, Depends(db_session_dep)],
            user_id: Annotated[str, Depends(self.user_oauth_integrator.user_authorizer.get_current_user_id)],
            request: Request,
            response: Response,
        ):
            band_form: StarletteForm = await BandForm.from_formdata(request)
            if await band_form.validate_on_submit():
                band_form_dict = band_form.data.copy()
                band_schema = BandSchema(**band_form_dict)
                band = Band(**band_schema.model_dump())
                band_id: int = band.insert(db_session)
                response.status_code = 201

                await self.user_oauth_integrator.user_authorizer_fga.add_permissions(
                    request, ["can_delete", "can_update"], "band", band_id
                )

                return {"id": band_id}

            html = templates.TemplateResponse("band_form.html", {"form": band_form, "request": request})
            return html

        if override_security_dependencies:

            async def dummy_is_authorized_current_user():
                return await await_true()

            async def await_true():
                future = asyncio.Future()
                return future

            app.dependency_overrides[
                self.user_oauth_integrator.user_authorizer.is_authorized_current_user
            ] = dummy_is_authorized_current_user
            app.dependency_overrides[
                self.user_oauth_integrator.user_authorizer_fga.is_authorized_current_user
            ] = dummy_is_authorized_current_user

        self.app = app
        return self.app
