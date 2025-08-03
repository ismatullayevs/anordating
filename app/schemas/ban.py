from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BanInSchema(BaseModel):
    user_telegram_id: int
    reason: str
    expires_at: Optional[datetime] = None


class BanOutSchema(BaseModel):
    id: int
    user_telegram_id: int
    reason: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class BanUpdateSchema(BaseModel):
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None
