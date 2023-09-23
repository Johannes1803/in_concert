from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int | None = None
    sub: str

    class Config:
        orm_mode = True
