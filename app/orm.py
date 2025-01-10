from sqlalchemy import select
from app.core.db import session_factory
from app.models.user import User


async def get_user(id: int):
    async with session_factory() as session:
        query = select(User).where(User.id == id)
        res = await session.scalars(query)
        return res.one_or_none()


async def get_user_by_telegram_id(telegram_id: int):
    async with session_factory() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        res = await session.scalars(query)
        return res.one_or_none()