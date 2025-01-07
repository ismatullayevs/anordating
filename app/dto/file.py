from pydantic import BaseModel
from app.enums import FileTypes
import datetime


class FileAddDTO(BaseModel):
    telegram_id: int | None
    telegram_unique_id: str | None
    telegram_path: str | None
    path: str | None
    file_type: FileTypes


class FileDTO(FileAddDTO):
    id: int
    uploaded_at: datetime.datetime
