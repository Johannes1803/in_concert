from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from definitions import PROJECT_ROOT


class Auth0Settings(BaseSettings):
    """Class holding the configuration for the user authentication api.

    Populate it by defining a .env file in the root directory of the project.
    """

    client_id: SecretStr = Field(alias="auth0_client_id")
    client_secret: SecretStr = Field(alias="auth0_client_secret")
    domain: str = Field(alias="auth0_domain")
    app_secret_key: SecretStr = Field()

    audience: Optional[str] = Field(alias="auth0_audience", default="https://in-concert-api.com")
    algorithms: SecretStr = Field()
    issuer: str = Field()
    grant_type: str = Field(default="client_credentials")

    middleware_secret_key: SecretStr = Field(alias="secret_middleware")

    db_connection_string: SecretStr = Field(alias="DB_CONNECTION_STRING")

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


class Auth0SettingsTest(Auth0Settings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env.test", extra="ignore")


class Auth0SettingsDev(Auth0Settings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env.dev", extra="ignore")
