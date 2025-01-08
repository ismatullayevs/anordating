from pydantic import BaseModel
from app.enums import FileTypes
import datetime
from app.models.file import File


class FileAddDTO(BaseModel):
    telegram_id: str | None
    telegram_unique_id: str | None
    path: str | None
    file_type: FileTypes
    file_size: int | None
    mime_type: str | None
    duration: int | None

    class Meta:
        orm_model = File


class FileRelThumbnailAddDTO(FileAddDTO):
    thumbnail: FileAddDTO | None


class FileDTO(FileAddDTO):
    id: int
    uploaded_at: datetime.datetime


class FileRelThumbnailDTO(FileDTO):
    thumbnail: FileDTO | None