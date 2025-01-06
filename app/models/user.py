from sqlalchemy.orm import mapped_column, Mapped
from app.core.db import Base
from typing import Annotated
import datetime
from sqlalchemy import text


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"),
    onupdate=datetime.datetime.now(datetime.timezone.utc))]


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int]
    name: Mapped[str]
    age: Mapped[int]

    created_at: Mapped[datetime.datetime]
    updated_at: Mapped[datetime.datetime]
