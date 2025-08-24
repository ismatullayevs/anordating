from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql import or_

from app.core.config import Settings
from app.enums import ReactionType
from app.exceptions import RewindLimitExceededError
from app.models.user import Ban, Reaction, Report, User


async def get_matches(
    user_id: UUID,
    db: AsyncSession,
    limit: int,
    offset: int,
) -> list[User]:
    """Get matches for a user."""
    their_reaction = aliased(Reaction)
    my_reaction = aliased(Reaction)

    query = (
        select(User)
        .join(
            my_reaction,
            and_(
                my_reaction.from_user_id == user_id,
                my_reaction.to_user_id == User.id,
                my_reaction.reaction_type == ReactionType.like,
            ),
        )
        .join(
            their_reaction,
            and_(
                their_reaction.from_user_id == User.id,
                their_reaction.to_user_id == user_id,
                their_reaction.reaction_type == ReactionType.like,
            ),
        )
        .where(
            User.is_active,
            ~exists().where(
                and_(
                    Report.from_user_id == user_id,
                    Report.to_user_id == User.id,
                ),
            ),
            ~exists().where(
                and_(
                    Report.from_user_id == User.id,
                    Report.to_user_id == user_id,
                ),
            ),
            ~exists().where(
                and_(
                    Ban.user_telegram_id == User.telegram_id,
                    or_(Ban.expires_at.is_(None), Ban.expires_at > func.now()),
                ),
            ),
        )
        .order_by(
            func.greatest(my_reaction.updated_at, their_reaction.updated_at).desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    return list((await db.scalars(query)).all())


async def get_rewinds(
    user_id: UUID,
    db: AsyncSession,
    limit: int,
    offset: int,
) -> Sequence[User]:
    """Get rewinds for a user."""
    if limit + offset >= Settings.REWIND_LIMIT:
        raise RewindLimitExceededError("Rewind limit exceeded")

    result = await db.scalars(
        select(User)
        .join(Reaction, Reaction.to_user_id == User.id)
        .where(and_(Reaction.from_user_id == user_id, User.is_active))
        .order_by(Reaction.updated_at.desc())
        .limit(limit)
        .offset(offset),
    )
    return result.all()
