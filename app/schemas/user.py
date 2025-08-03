from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator

from app.enums import Genders, UILanguages
from app.validators import validate_bio, validate_birth_date, validate_name


class UserInSchema(BaseModel):
    telegram_id: int
    name: Annotated[str, AfterValidator(validate_name)]
    birth_date: Annotated[datetime, BeforeValidator(validate_birth_date)]
    bio: Annotated[str | None, AfterValidator(validate_bio)]
    gender: Genders
    latitude: float
    longitude: float
    ui_language: UILanguages
    is_location_precise: bool
    place_id: str | None = None


class UserOutSchema(UserInSchema):
    id: int
    rating: int
    is_active: bool
