from sqlalchemy.orm import mapped_column, Mapped
from app.models.base import Base, intpk, created_at, updated_at
from sqlalchemy import text, String
from app.core.config import settings


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[intpk]
    telegram_id: Mapped[int]
    name: Mapped[str]
    age: Mapped[int]
    rating: Mapped[int] = mapped_column(server_default=text(str(settings.DEFAULT_RATING)))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    bio: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
