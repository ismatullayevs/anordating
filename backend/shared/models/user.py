import uuid
from datetime import date, datetime

from sqlalchemy import BIGINT, ForeignKey, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.core.config import settings
from shared.enums import (
    Genders,
    PreferredGenders,
    ReactionType,
    ReportStatusTypes,
    UILanguages,
)
from shared.models.base import Base, created_at, intpk, updated_at
from shared.models.file import File


class Place(Base):
    __tablename__ = "place"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    users: Mapped[list["User"]] = relationship("User", back_populates="place")
    names: Mapped[list["PlaceName"]] = relationship("PlaceName", back_populates="place")


class PlaceName(Base):
    __tablename__ = "place_name"

    id: Mapped[intpk]
    place_id: Mapped[str] = mapped_column(
        ForeignKey("place.id", ondelete="CASCADE"), index=True
    )
    language: Mapped[UILanguages]
    name: Mapped[str]

    place: Mapped[Place] = relationship("Place", back_populates="names")

    __table_args__ = (UniqueConstraint("place_id", "language"),)


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, index=True)
    name: Mapped[str]
    birth_date: Mapped[datetime]
    rating: Mapped[int] = mapped_column(
        server_default=text(str(settings.DEFAULT_RATING))
    )
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    bio: Mapped[str | None] = mapped_column(String(255))
    media: Mapped[list[File]] = relationship(secondary="user_media")
    gender: Mapped[Genders]

    latitude: Mapped[float]
    longitude: Mapped[float]
    place_id: Mapped[str | None] = mapped_column(
        ForeignKey("place.id", ondelete="SET NULL"), index=True
    )
    place: Mapped[Place | None] = relationship("Place", back_populates="users")
    is_location_precise: Mapped[bool] = mapped_column(server_default=text("true"))

    ui_language: Mapped[UILanguages]
    phone_number: Mapped[str]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    preferences: Mapped["Preferences"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    chat_members: Mapped["ChatMember"] = relationship(back_populates="user")  # type: ignore

    is_superuser: Mapped[bool] = mapped_column(server_default=text("false"))

    @hybrid_property
    def age(self) -> int:
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @age.inplace.expression
    @classmethod
    def _age_expression(cls):
        return func.date_part("year", func.age(func.current_date(), cls.birth_date))


class Preferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[intpk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True, unique=True
    )
    min_age: Mapped[int | None] = mapped_column(index=True)
    max_age: Mapped[int | None] = mapped_column(index=True)
    preferred_gender: Mapped[PreferredGenders] = mapped_column(index=True)

    user = relationship("User", back_populates="preferences")


class Reaction(Base):
    __tablename__ = "reaction"

    id: Mapped[intpk]
    from_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True
    )
    to_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True
    )
    reaction_type: Mapped[ReactionType] = mapped_column(index=True)
    is_match_notified: Mapped[bool] = mapped_column(server_default=text("false"))
    added_rating: Mapped[int]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    __table_args__ = (UniqueConstraint("from_user_id", "to_user_id"),)


class Report(Base):
    __tablename__ = "report"

    id: Mapped[intpk]
    from_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True
    )
    to_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True
    )
    reason: Mapped[str]
    status: Mapped[ReportStatusTypes] = mapped_column(
        index=True, server_default=text("'pending'")
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
