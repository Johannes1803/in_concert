from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)
