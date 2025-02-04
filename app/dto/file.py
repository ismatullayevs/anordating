import datetime
from typing import Annotated

from pydantic import AfterValidator

from app.dto.base import BaseModelWithOrm
from app.enums import FileTypes
from app.models.file import File
from app.validators import validate_video_duration


class FileAddDTO(BaseModelWithOrm[File]):
    telegram_id: str | None
    telegram_unique_id: str | None
    path: str | None
    file_type: FileTypes
    file_size: int | None
    mime_type: str | None
    duration: Annotated[int | None, AfterValidator(validate_video_duration)]

    @property
    def orm_model(self):
        return File


class FileRelThumbnailAddDTO(FileAddDTO):
    thumbnail: FileAddDTO | None


class FileDTO(FileAddDTO):
    id: int
    uploaded_at: datetime.datetime


class FileRelThumbnailDTO(FileDTO):
    thumbnail: FileDTO | None
