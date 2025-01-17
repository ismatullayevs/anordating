from app.matching.rating import update_rating
from app.models.user import Reaction, User
from app.core.db import session_factory
from app.enums import ReactionType
from sqlalchemy import and_, exists, select, exc
from sqlalchemy.orm import selectinload, joinedload, aliased


async def get_user(id: int | None = None, telegram_id: int | None = None, 
                   is_active: bool | None = None, with_media=False, with_preferences=False):
    async with session_factory() as session:
        query = select(User)
        if id:
            query = query.where(User.id == id)
        else:
            query = query.where(User.telegram_id == telegram_id)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        if with_media:
            query = query.options(selectinload(User.media))
        if with_preferences:
            query = query.options(joinedload(User.preferences))

        res = await session.scalars(query)
        return res.one()


async def get_likes(user: User, limit: int | None = None):
    async with session_factory() as session:
        their_reaction = aliased(Reaction)
        my_reaction = aliased(Reaction)

        query = (
            select(User)
            .join(
                their_reaction,
                and_(
                    their_reaction.from_user_id == User.id,
                    their_reaction.to_user_id == user.id,
                    their_reaction.reaction_type == ReactionType.like
                )
            )
            .where(
                User.is_active == True,
                ~exists().where(
                    and_(
                        my_reaction.from_user_id == user.id,
                        my_reaction.to_user_id == User.id,
                    )
                )
            )
            .order_by(their_reaction.updated_at.desc())
        )
        if limit:
            query = query.limit(limit)

        res = await session.scalars(query)
        return res.all()


async def create_or_update_reaction(user: User, match: User, reaction_type: ReactionType):
    async with session_factory() as session:
        session.add_all((user, match))
        res = await session.scalars(select(Reaction)
                                    .where(Reaction.from_user_id == user.id,
                                           Reaction.to_user_id == match.id))
        try:
            reaction = res.one()
            if reaction.reaction_type == reaction_type:
                raise ValueError("Reaction already exists")
            reaction.reaction_type = reaction_type
        except exc.NoResultFound:
            reaction = Reaction(from_user_id=user.id,
                                to_user_id=match.id,
                                reaction_type=reaction_type)

        match.rating = update_rating(match.rating, user.rating, reaction_type)
        session.add(reaction)
        await session.commit()
    return reaction
