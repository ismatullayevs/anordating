from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, model_validator

from app.dto.base import BaseModelWithOrm
from app.dto.file import FileAddDTO, FileDTO
from app.enums import Genders, PreferredGenders, ReactionType, UILanguages
from app.models.user import Place, Preferences, Reaction, Report, User
from app.validators import (
    validate_bio,
    validate_birth_date,
    validate_media_size,
    validate_name,
    validate_preference_age,
    validate_preference_ages,
)


class PreferenceAddDTO(BaseModelWithOrm[Preferences]):
    min_age: Annotated[int | None, AfterValidator(validate_preference_age)]
    max_age: Annotated[int | None, AfterValidator(validate_preference_age)]
    preferred_gender: PreferredGenders

    @model_validator(mode="after")
    def validate_min_max_age(self):
        min_age, max_age = validate_preference_ages(self.min_age, self.max_age)
        self.min_age, self.max_age = min_age, max_age
        return self

    @property
    def orm_model(self):
        return Preferences


class PreferenceDTO(PreferenceAddDTO):
    user_id: int


class PlaceAddDTO(BaseModelWithOrm[Place]):
    id: str

    @property
    def orm_model(self):
        return Place


class UserAddDTO(BaseModelWithOrm[User]):
    telegram_id: int
    name: Annotated[str, AfterValidator(validate_name)]
    birth_date: Annotated[datetime, BeforeValidator(validate_birth_date)]
    bio: Annotated[str | None, AfterValidator(validate_bio)]
    gender: Genders
    latitude: float
    longitude: float
    ui_language: UILanguages
    phone_number: str
    is_location_precise: bool

    @property
    def orm_model(self):
        return User


class UserRelMediaAddDTO(UserAddDTO):
    media: Annotated[list[FileAddDTO], AfterValidator(validate_media_size)]


class UserRelPreferencesAddDTO(UserAddDTO):
    preferences: PreferenceAddDTO


class UserRelAddDTO(UserAddDTO):
    media: list[FileAddDTO]
    preferences: PreferenceAddDTO


class UserDTO(UserAddDTO):
    id: str
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
