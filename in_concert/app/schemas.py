from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    # id: int | None = None
    sub: str

    model_config = ConfigDict(from_attributes=True)
