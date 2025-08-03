from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserInSchema


async def register_user(db: AsyncSession, user_data: UserInSchema) -> User:
    """Registers a new user in the database."""
    # TODO: Validate that user has media files when using the app
    try:
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        return user
    except Exception as e:
        await db.rollback()
        raise e


async def get_user(db: AsyncSession, user_id: UUID) -> User:
    """Fetches a user by ID or Telegram ID."""
    result = await db.scalar(
        select(User).where(
            (User.id == user_id),
        )
    )
    if not result:
        raise ValueError("User not found")
    return result


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User:
    """Fetches a user by Telegram ID."""
    user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
    if not user:
        raise ValueError("User not found")
    return user
