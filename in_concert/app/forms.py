from starlette_wtf import StarletteForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, Length


class VenueForm(StarletteForm):
    name = StringField("name", validators=[DataRequired(), Length(min=2, max=30)])
    street = StringField("street", validators=[DataRequired(), Length(max=30)])
    city = StringField("city", validators=[DataRequired(), Length(max=30)])
    zip_code = IntegerField("zip_code", validators=[DataRequired()])
    state = StringField("state", validators=[DataRequired(), Length(max=30)])
    phone = IntegerField("phone", validators=[DataRequired()])
    website = StringField("website", validators=[Length(max=30)])
    image_link = StringField("image_link", validators=[Length(max=30)])
    genres = StringField("genres", validators=[Length(max=30)])
