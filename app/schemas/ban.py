from datetime import datetime

from pydantic import BaseModel


class BanInSchema(BaseModel):
    user_telegram_id: int
    reason: str
    expires_at: datetime | None = None


class BanOutSchema(BaseModel):
    id: int
    user_telegram_id: int
    reason: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None


class BanUpdateSchema(BaseModel):
    reason: str | None = None
    expires_at: datetime | None = None
