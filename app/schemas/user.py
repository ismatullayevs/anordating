from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator

from app.enums import FileTypes, Genders, UILanguages
from app.validators import validate_bio, validate_birth_date, validate_name


class FileInSchema(BaseModel):
    telegram_id: str | None = None
    telegram_unique_id: str | None = None
    file_type: FileTypes
    file_size: int | None = None
    mime_type: str | None = None
    thumbnail: "FileInSchema | None" = None
    duration: int | None = None


class FileOutSchema(FileInSchema):
    id: int
    uploaded_at: datetime
    path: str | None


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
