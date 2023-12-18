from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)
    venues: Optional[list[int]] = Field(default_factory=list)


class VenueSchema(BaseModel):
    name: str
    street: str
    city: str
    state: str
    zip_code: int
    phone: int
    website: Optional[str] = None
    image_link: Optional[str] = None
    genres: Optional[str] = None
    manager_id: str
    about: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BandSchema(BaseModel):
    name: str
    city: Optional[str] = None
    zip_code: Optional[int] = None
    state: Optional[str] = None
    website_link: Optional[str] = None
    image_link: Optional[str] = None
    genres: Optional[str] = None
    manager_id: str
