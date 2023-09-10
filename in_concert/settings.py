from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from definitions import PROJECT_ROOT


class Auth0Settings(BaseSettings):
    """Class holding the configuration for the user authentication api.

    Populate it by defining a .env file in the root directory of the project.
    """

    client_id: str = Field(alias="auth0_client_id")
    client_secret: str = Field(alias="auth0_client_secret")
    domain: str = Field(alias="auth0_domain")
    app_secret_key: str = Field()

    audience: Optional[str] = Field(alias="auth0_audience", default="https://in-concert-api.com")
    algorithms: str = Field()
    issuer: str = Field()
    grant_type: str = Field(default="client_credentials")

    middleware_secret_key: str = Field(alias="secret_middleware")

    db_connection_string: str = Field(alias="DB_CONNECTION_STRING")

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class Auth0SettingsTest(Auth0Settings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env.test", extra="ignore")


class Auth0SettingsDev(Auth0Settings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env.dev", extra="ignore")
