from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, created_at, intpk, updated_at
from shared.models.user import User


class Chat(Base):
    __tablename__ = "chat"

    members: Mapped["ChatMember"] = relationship(back_populates="chat")

    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class ChatMember(Base):
    __tablename__ = "chat_member"

    id: Mapped[intpk]
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["User"] = relationship(back_populates="chat_members")
    chat: Mapped["Chat"] = relationship(back_populates="members")

    __table_args__ = (UniqueConstraint("user_id", "chat_id"),)


class Message(Base):
    __tablename__ = "message"

    id: Mapped[intpk]
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), index=True
    )

    text: Mapped[str]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
