from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel

from app.dto.base import BaseModelWithOrm
from app.models.chat import Chat, Message
from app.validators import validate_message_text


class ChatInDTO(BaseModel):
    match_id: str


class ChatDTO(BaseModelWithOrm[Chat]):
    id: int
    created_at: datetime
    updated_at: datetime


class MessageBaseDTO(BaseModelWithOrm[Message]):
    text: Annotated[str, AfterValidator(validate_message_text)]

    @property
    def orm_model(self):
        return Message


class MessageInDTO(MessageBaseDTO):
    pass


class MessageAddDTO(MessageBaseDTO):
    chat_id: int
    user_id: UUID


class MessageDTO(MessageAddDTO):
    id: int
    created_at: datetime
    updated_at: datetime


class ChatMemberDTO(BaseModel):
    user_id: UUID
    chat_id: int
    created_at: datetime
    updated_at: datetime
