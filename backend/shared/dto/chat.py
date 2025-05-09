from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shared.dto.base import BaseModelWithOrm
from shared.models.chat import Chat, Message


class ChatInDTO(BaseModel):
    match_id: str


class ChatDTO(BaseModelWithOrm[Chat]):
    id: int
    created_at: datetime
    updated_at: datetime


class MessageBaseDTO(BaseModelWithOrm[Message]):
    text: str

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