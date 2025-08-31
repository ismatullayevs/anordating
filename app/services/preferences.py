from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import Preferences, User
from app.schemas.preferences import PreferencesInSchema


async def get_user_preferences(db: AsyncSession, user_id: UUID) -> Preferences:
    """Fetch user preferences."""
    result = await db.scalars(select(User.preferences).where(User.id == user_id))
    return result.one()


async def create_user_preferences(
    db: AsyncSession,
    user_id: UUID,
    preferences_data: PreferencesInSchema,
) -> Preferences:
    """Create user preferences."""
    try:
        preferences = Preferences(user_id=user_id, **preferences_data.model_dump())
        db.add(preferences)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return preferences


async def update_user_preferences(
    db: AsyncSession,
    user_id: UUID,
    preferences_data: PreferencesInSchema,
) -> Preferences:
    """Update user preferences."""
    try:
        preferences = await get_user_preferences(db, user_id)
        for key, value in preferences_data.model_dump().items():
            setattr(preferences, key, value)
        db.add(preferences)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return preferences
