from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.models.base import Base, intpk, created_at, updated_at
from sqlalchemy import text, String, BIGINT, ForeignKey, UniqueConstraint
from app.core.config import settings
from app.enums import Genders, PreferredGenders, UILanguages, ReactionType, ReportStatusTypes
from app.models.file import File


class User(AsyncAttrs, Base):
    __tablename__ = "user_account"

    id: Mapped[intpk]
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, index=True)
    name: Mapped[str]
    age: Mapped[int] = mapped_column(index=True)
    rating: Mapped[int] = mapped_column(
        server_default=text(str(settings.DEFAULT_RATING)))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    bio: Mapped[str | None] = mapped_column(String(255))
    media: Mapped[list[File]] = relationship(
        secondary="user_media")
    gender: Mapped[Genders]
    latitude: Mapped[float]
    longitude: Mapped[float]

    ui_language: Mapped[UILanguages]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    preferences: Mapped["Preferences"] = relationship(
        back_populates="user", cascade="all, delete-orphan")


class Preferences(AsyncAttrs, Base):
    __tablename__ = "user_preferences"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "user_account.id", ondelete="CASCADE"), index=True, unique=True)
    min_age: Mapped[int | None] = mapped_column(index=True)
    max_age: Mapped[int | None] = mapped_column(index=True)
    preferred_gender: Mapped[PreferredGenders] = mapped_column(index=True)

    user = relationship("User", back_populates="preferences")


class Reaction(AsyncAttrs, Base):
    __tablename__ = "reaction"

    id: Mapped[intpk]
    from_user_id: Mapped[int] = mapped_column(ForeignKey(
        "user_account.id", ondelete="CASCADE"), index=True)
    to_user_id: Mapped[int] = mapped_column(ForeignKey(
        "user_account.id", ondelete="CASCADE"), index=True)
    reaction_type: Mapped[ReactionType] = mapped_column(index=True)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    __table_args__ = (UniqueConstraint("from_user_id", "to_user_id"),)


class Report(AsyncAttrs, Base):
    __tablename__ = "report"

    id: Mapped[intpk]
    from_user_id: Mapped[int] = mapped_column(ForeignKey(
        "user_account.id", ondelete="CASCADE"), index=True)
    to_user_id: Mapped[int] = mapped_column(ForeignKey(
        "user_account.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str]
    status: Mapped[ReportStatusTypes] = mapped_column(index=True)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
