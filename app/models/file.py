from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from app.models.base import Base, intpk, created_at
from sqlalchemy import String
from app.enums import FileTypes


class File(Base):
    __tablename__ = "file"

    id: Mapped[intpk]
    telegram_id: Mapped[str | None] = mapped_column(String(255), index=True)
    telegram_unique_id: Mapped[str | None] = mapped_column(String(255))
    path: Mapped[str | None]
    file_type: Mapped[FileTypes]
    file_size: Mapped[int | None]
    mime_type: Mapped[str | None]
    thumbnail_id: Mapped[int | None] = mapped_column(ForeignKey("file.id", ondelete="SET NULL"))
    duration: Mapped[int | None]
    uploaded_at: Mapped[created_at]

    thumbnail: Mapped["File"] = relationship("File")


class UserMedia(Base):
    __tablename__ = "user_media"

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("file.id", ondelete="CASCADE"), primary_key=True)

    __table_args__ = (UniqueConstraint("user_id", "file_id"),)
