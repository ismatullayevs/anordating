from datetime import datetime
from app.enums import Genders, ReactionType, UILanguages, PreferredGenders
from app.dto.file import FileDTO, FileAddDTO
from app.models.user import Preferences, Reaction, User, Report
from pydantic import BaseModel, AfterValidator
from typing import Annotated, Type
from aiogram.utils.i18n import gettext as _
from app.validators import validate_age, validate_media_length, validate_name, validate_preferred_max_age, validate_preferred_min_age
from app.dto.base import BaseModelWithOrm


class PreferenceAddDTO(BaseModelWithOrm[Preferences]):
    min_age: Annotated[int | None, AfterValidator(validate_preferred_min_age)]
    max_age: Annotated[int | None, AfterValidator(validate_preferred_max_age)]
    preferred_gender: PreferredGenders

    @property
    def orm_model(self):
        return Preferences


class PreferenceDTO(PreferenceAddDTO):
    user_id: int


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
