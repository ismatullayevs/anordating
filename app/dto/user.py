from pydantic import BaseModel
from app.enums import Genders, UILanguages, PreferredGenders
from datetime import datetime
from app.dto.file import FileDTO, FileAddDTO
from app.models.user import User


class PreferenceDTO(BaseModel):
    user_id: int
    min_age: int | None
    max_age: int | None
    preferred_gender: PreferredGenders


class UserAddDTO(BaseModel):
    telegram_id: int
    name: str
    age: int
    bio: str | None
    gender: Genders
    latitude: float
    longitude: float
    ui_language: UILanguages

    class Meta:
        orm_mode = True
        orm_model = User


class UserRelMediaAddDTO(UserAddDTO):
    media: list[FileAddDTO]


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
