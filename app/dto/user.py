from datetime import datetime
from app.enums import Genders, UILanguages, PreferredGenders
from app.dto.file import FileDTO, FileAddDTO
from app.models.user import User
from pydantic import BaseModel, AfterValidator
from typing import Annotated, Type
from aiogram.utils.i18n import gettext as _
from app.validators import validate_age, validate_media_length, validate_name
from app.dto.base import BaseModelWithOrm


class PreferenceDTO(BaseModel):
    user_id: int
    min_age: int | None
    max_age: int | None
    preferred_gender: PreferredGenders


class UserAddDTO(BaseModelWithOrm[User]):
    telegram_id: int
    name: Annotated[str, AfterValidator(validate_name)]
    age: Annotated[int, AfterValidator(validate_age)]
    bio: str | None
    gender: Genders
    latitude: float
    longitude: float
    ui_language: UILanguages

    @property
    def orm_model(self):
        return User


class UserRelMediaAddDTO(UserAddDTO):
    media: Annotated[list[FileAddDTO], AfterValidator(validate_media_length)]


class UserDTO(UserAddDTO):
    id: int
    rating: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserRelMediaDTO(UserDTO):
    media: list[FileDTO]


class UserRelPreferencesDTO(UserDTO):
    preferences: PreferenceDTO


class UserRelDTO(UserDTO):
    media: list[FileDTO]
    preferences: PreferenceDTO
