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
    website: str
    image_link: str
    genres: str

    model_config = ConfigDict(from_attributes=True)
