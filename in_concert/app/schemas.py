from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)


class VenueManagerSchema(UserSchema):
    venues: Optional[list[int]] = Field(default_factory=list)


class VenueSchema(BaseModel):
    name: str
    street: str
    city: str
    state: str
    zip_code: int
    phone: int
    website: Optional[str]
    image_link: Optional[str]
    genres: Optional[str]
    manager_id: int

    model_config = ConfigDict(from_attributes=True)
