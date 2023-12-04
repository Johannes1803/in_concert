from typing import Optional

from pydantic import Field, SecretStr
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
    db_connection_string: SecretStr = Field()

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class FGAAuthSettings(BaseSettings):
    fga_api_scheme: str = Field()
    fga_api_host: str = Field()
    fga_store_id: str = Field()
    fga_api_token_issuer: str = Field()
    fga_api_audience: str = Field()
    fga_client_id: str = Field()
    fga_client_secret: str = Field()


class AppSettings(Auth0Settings, FGAAuthSettings):
    pass


class AppSettingsTest(AppSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env.test", extra="ignore")


class AppSettingsDev(AppSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env.dev", extra="ignore")
