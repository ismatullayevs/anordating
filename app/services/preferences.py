from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User


async def get_user_preferences(db: AsyncSession, user_id: UUID):
    """Fetches user preferences."""
    result = await db.scalar(select(User.preferences).where(User.id == user_id))
    if not result:
        raise ValueError("User preferences not found")
    return result
