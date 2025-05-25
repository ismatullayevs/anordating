from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel

from shared.validators import validate_message_text
from shared.dto.base import BaseModelWithOrm
from shared.models.chat import Chat, Message


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
