from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from shared.models.base import Base, created_at, updated_at, intpk


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class ChatMember(Base):
    __tablename__ = "chat_member"

    id: Mapped[intpk]
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(
        "user_account.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    __table_args__ = (UniqueConstraint("user_id", "chat_id"),)


class Message(Base):
    __tablename__ = "message"

    id: Mapped[intpk]
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(
        "user_account.id", ondelete="CASCADE"), index=True)
    
    text: Mapped[str]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]