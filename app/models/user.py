from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects import postgresql
from app.models.base import Base, intpk, created_at, updated_at
from sqlalchemy import text, String, BIGINT, ForeignKey
from app.core.config import settings
from app.dto.enums import Genders, PreferredGenders, UILanguages


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[intpk]
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, index=True)
    name: Mapped[str]
    age: Mapped[int] = mapped_column(index=True)
    rating: Mapped[int] = mapped_column(server_default=text(str(settings.DEFAULT_RATING)))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    bio: Mapped[str | None] = mapped_column(String(255))
    media: Mapped[list["File"]] = relationship(secondary="user_media", backref="users") # type: ignore
    gender: Mapped[Genders]
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]

    ui_language: Mapped[UILanguages]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    preferences = relationship("Preferences", uselist=False, back_populates="user")


class Preferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    min_age: Mapped[int | None] = mapped_column(index=True)
    max_age: Mapped[int | None] = mapped_column(index=True)
    preferred_gender: Mapped[PreferredGenders] = mapped_column(index=True)

    user = relationship("User", back_populates="preferences")
