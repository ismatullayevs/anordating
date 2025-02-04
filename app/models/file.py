import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import FileTypes
from app.models.base import Base, created_at, intpk


class File(Base):
    __tablename__ = "file"

    id: Mapped[intpk]
    telegram_id: Mapped[str | None] = mapped_column(String(255), index=True)
    telegram_unique_id: Mapped[str | None] = mapped_column(String(255))
    path: Mapped[str | None]
    file_type: Mapped[FileTypes]
    file_size: Mapped[int | None]
    mime_type: Mapped[str | None]
    thumbnail_id: Mapped[int | None] = mapped_column(
        ForeignKey("file.id", ondelete="SET NULL")
    )
    duration: Mapped[int | None]
    uploaded_at: Mapped[created_at]

    thumbnail: Mapped["File"] = relationship("File")


class UserMedia(Base):
    __tablename__ = "user_media"

    id: Mapped[intpk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True
    )
    file_id: Mapped[int] = mapped_column(
        ForeignKey("file.id", ondelete="CASCADE"), index=True
    )

    __table_args__ = (UniqueConstraint("user_id", "file_id"),)
