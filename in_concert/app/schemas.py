from pydantic import BaseModel, ConfigDict

from in_concert.app.models import User


class UserSchema(BaseModel):
    # id: int | None = None
    sub: str

    model_config = ConfigDict(from_attributes=True)
