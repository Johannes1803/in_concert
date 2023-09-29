from pydantic import BaseModel, ConfigDict


class OauthTokenSchema(BaseModel):
    access_token: str
    token_type: str

    model_config = ConfigDict(extra="allow")
