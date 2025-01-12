from datetime import datetime

from annotated_types import Ge, Le
from app.enums import Genders, ReactionType, UILanguages, PreferredGenders
from app.dto.file import FileDTO, FileAddDTO
from app.models.user import Preferences, Reaction, User, Report
from pydantic import Field, field_validator, model_validator
from typing import Annotated
from aiogram.utils.i18n import gettext as _
from app.dto.base import BaseModelWithOrm


class PreferenceAddDTO(BaseModelWithOrm[Preferences]):
    min_age: Annotated[int | None, Field(ge=18, le=100)]
    max_age: Annotated[int | None, Field(ge=18, le=100)]
    preferred_gender: PreferredGenders

    @model_validator(mode="after")
    def validate_min_max_age(self):
        if self.min_age and self.max_age:
            if self.min_age > self.max_age:
                raise ValueError("Min age must be less than max age")
        return self

    @property
    def orm_model(self):
        return Preferences


class PreferenceDTO(PreferenceAddDTO):
    user_id: int


class UserAddDTO(BaseModelWithOrm[User]):
    telegram_id: int
    name: Annotated[str, Field(max_length=30, min_length=3)]
    age: Annotated[int, Field(ge=18, le=100)]
    bio: Annotated[str | None, Field(max_length=255)]
    gender: Genders
    latitude: float
    longitude: float
    ui_language: UILanguages

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, value: str):
        if not (value and all(x.isalpha() or x.isspace() for x in value)):
            raise ValueError(_("Name must not contain digits"))
        return value

    @property
    def orm_model(self):
        return User


class UserRelMediaAddDTO(UserAddDTO):
    media: Annotated[list[FileAddDTO], Ge(1), Le(3)]


class UserRelPreferencesAddDTO(UserAddDTO):
    preferences: PreferenceAddDTO


class UserRelAddDTO(UserAddDTO):
    media: list[FileAddDTO]
    preferences: PreferenceAddDTO


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


class ReactionAddDTO(BaseModelWithOrm[Reaction]):
    from_user_id: int
    to_user_id: int
    reaction_type: ReactionType

    @property
    def orm_model(self):
        return Reaction


class ReactionDTO(ReactionAddDTO):
    id: int
    created_at: datetime
    updated_at: datetime


class ReportAddDTO(BaseModelWithOrm[Report]):
    from_user_id: int
    to_user_id: int
    reason: str

    @property
    def orm_model(self):
        return Report


class ReportDTO(ReportAddDTO):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
