from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Ban
from app.schemas.ban import BanInSchema, BanUpdateSchema


async def create_ban(db: AsyncSession, ban_data: BanInSchema) -> Ban:
    """Creates a new ban."""
    try:
        now = datetime.now(timezone.utc)
        existing_ban = await db.scalar(
            select(Ban).where(
                and_(
                    Ban.user_telegram_id == ban_data.user_telegram_id,
                    (Ban.expires_at.is_(None) | (Ban.expires_at > now))
                )
            )
        )
        if existing_ban:
            raise ValueError("Active ban already exists for this user")

        ban = Ban(
            user_telegram_id=ban_data.user_telegram_id,
            reason=ban_data.reason,
            expires_at=ban_data.expires_at
        )
        db.add(ban)
        await db.commit()
        await db.refresh(ban)
        return ban
    except Exception as e:
        await db.rollback()
        raise e


async def get_bans(
    db: AsyncSession,
    user_telegram_id: Optional[int] = None,
    active_only: bool = False,
    limit: int = 100,
    offset: int = 0
) -> list[Ban]:
    """Fetches bans with optional filters."""
    query = select(Ban)
    
    if user_telegram_id:
        query = query.where(Ban.user_telegram_id == user_telegram_id)
    
    if active_only:
        now = datetime.utcnow()
        query = query.where(Ban.expires_at.is_(None) | (Ban.expires_at > now))
    
    query = query.order_by(Ban.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.scalars(query)
    return list(result.all())


async def get_ban_by_id(db: AsyncSession, ban_id: int) -> Ban | None:
    """Fetches a ban by ID."""
    return await db.scalar(select(Ban).where(Ban.id == ban_id))


async def get_active_ban_by_telegram_id(db: AsyncSession, telegram_id: int) -> Ban | None:
    """Fetches active ban for a user by telegram ID."""
    now = datetime.now(timezone.utc)
    return await db.scalar(
        select(Ban).where(
            and_(
                Ban.user_telegram_id == telegram_id,
                (Ban.expires_at.is_(None) | (Ban.expires_at > now))
            )
        )
    )


async def update_ban(
    db: AsyncSession, ban_id: int, update_data: BanUpdateSchema
) -> Ban:
    """Updates a ban."""
    try:
        ban = await db.scalar(select(Ban).where(Ban.id == ban_id))
        if not ban:
            raise ValueError("Ban not found")
        
        if update_data.reason is not None:
            ban.reason = update_data.reason
        if update_data.expires_at is not None:
            ban.expires_at = update_data.expires_at
        
        await db.commit()
        await db.refresh(ban)
        return ban
    except Exception as e:
        await db.rollback()
        raise e


async def delete_ban(db: AsyncSession, ban_id: int) -> None:
    """Deletes a ban (effectively unbanning the user)."""
    try:
        ban = await db.scalar(select(Ban).where(Ban.id == ban_id))
        if not ban:
            raise ValueError("Ban not found")
        
        await db.delete(ban)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def is_user_banned(db: AsyncSession, telegram_id: int) -> bool:
    """Checks if a user is currently banned."""
    ban = await get_active_ban_by_telegram_id(db, telegram_id)
    return ban is not None
