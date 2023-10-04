from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)


class VenueSchema(BaseModel):
    name: str
    address: str
    state: str
    zip_code: int
    phone: int
    website: Optional[str]
    image_link: Optional[str]
    genres: Optional[str]

    model_config = ConfigDict(from_attributes=True)
