from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, UniqueConstraint
from app.models.base import Base, intpk, created_at
from sqlalchemy import text, BIGINT
from app.dto.enums import FileTypes


class File(Base):
    __tablename__ = "file"

    id: Mapped[intpk]
    telegram_id: Mapped[int | None] = mapped_column(BIGINT, index=True)
    telegram_unique_id: Mapped[str | None]
    telegram_path: Mapped[str | None]
    path: Mapped[str | None]
    file_type: Mapped[FileTypes]
    uploaded_at: Mapped[created_at]


class UserMedia(Base):
    __tablename__ = "user_media"

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("file.id", ondelete="CASCADE"), primary_key=True)

    __table_args__ = (UniqueConstraint("user_id", "file_id"),)
