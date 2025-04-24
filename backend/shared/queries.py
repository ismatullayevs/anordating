from sqlalchemy import and_, exc, exists, func, select
from sqlalchemy.orm import aliased, joinedload, selectinload

from shared.core.db import session_factory
from shared.enums import ReactionType, UILanguages
from shared.geocoding import get_place
from shared.matching.rating import get_new_rating
from shared.models.user import PlaceName, Reaction, Report, User


async def get_user(
    id: str | None = None,
    telegram_id: int | None = None,
    is_active: bool | None = None,
    with_media=False,
    with_preferences=False,
):
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
                    their_reaction.reaction_type == ReactionType.like,
                ),
            )
            .where(
                User.is_active,
                ~exists().where(
                    and_(
                        my_reaction.from_user_id == user.id,
                        my_reaction.to_user_id == User.id,
                    )
                ),
                ~exists().where(
                    and_(
                        Report.from_user_id == user.id,
                        Report.to_user_id == User.id,
                    )
                ),
                ~exists().where(
                    and_(
                        Report.from_user_id == User.id,
                        Report.to_user_id == user.id,
                    )
                ),
            )
            .order_by(their_reaction.updated_at.desc())
        )

        if limit:
            query = query.limit(limit)

        res = await session.scalars(query)
        return res.all()


async def get_matches(user: User, limit: int | None = None, offset: int | None = None):
    async with session_factory() as session:
        their_reaction = aliased(Reaction)
        my_reaction = aliased(Reaction)

        query = (
            select(User)
            .join(
                my_reaction,
                and_(
                    my_reaction.from_user_id == user.id,
                    my_reaction.to_user_id == User.id,
                    my_reaction.reaction_type == ReactionType.like,
                ),
            )
            .join(
                their_reaction,
                and_(
                    their_reaction.from_user_id == User.id,
                    their_reaction.to_user_id == user.id,
                    their_reaction.reaction_type == ReactionType.like,
                ),
            )
            .where(
                User.is_active,
                ~exists().where(
                    and_(
                        Report.from_user_id == user.id,
                        Report.to_user_id == User.id,
                    )
                ),
                ~exists().where(
                    and_(
                        Report.from_user_id == User.id,
                        Report.to_user_id == user.id,
                    )
                ),
            )
            .order_by(
                func.greatest(my_reaction.updated_at, their_reaction.updated_at).desc()
            )
        )

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return (await session.scalars(query)).all()


async def create_or_update_reaction(
    user: User, match: User, reaction_type: ReactionType
):
    assert user.is_active and match.is_active
    async with session_factory() as session:
        res = await session.scalars(
            select(Reaction).where(
                Reaction.from_user_id == user.id, Reaction.to_user_id == match.id
            )
        )
        try:
            reaction = res.one()
            if reaction.reaction_type == reaction_type:
                return reaction

            previous_rating = match.rating - reaction.added_rating
            match.rating = get_new_rating(previous_rating, user.rating, reaction_type)

            reaction.reaction_type = reaction_type
            reaction.added_rating = match.rating - previous_rating
        except exc.NoResultFound:
            previous_rating = match.rating
            match.rating = get_new_rating(match.rating, user.rating, reaction_type)
            reaction = Reaction(
                from_user_id=user.id,
                to_user_id=match.id,
                reaction_type=reaction_type,
                added_rating=match.rating - previous_rating,
            )

        session.add_all((reaction, match))
        await session.commit()
    return reaction


async def get_nth_last_reacted_match(user: User, n: int):
    async with session_factory() as session:
        query = (
            select(User)
            .join(Reaction, Reaction.to_user_id == User.id)
            .where(and_(Reaction.from_user_id == user.id, User.is_active))
            .order_by(Reaction.updated_at.desc())
            .limit(1)
            .offset(n)
        )
        matches = (await session.scalars(query)).all()

    if not matches:
        return None

    return matches[0]


async def is_mutual(reaction: Reaction):
    if reaction.reaction_type != ReactionType.like:
        return False

    async with session_factory() as session:
        query = select(Reaction).where(
            Reaction.from_user_id == reaction.to_user_id,
            Reaction.to_user_id == reaction.from_user_id,
            Reaction.reaction_type == ReactionType.like,
        )
        res = await session.scalars(query)
        return res.one_or_none() is not None


async def get_city_name(user: User, language: UILanguages):
    if not user.place_id:
        return None

    async with session_factory() as session:
        query = select(PlaceName).where(
            PlaceName.place_id == user.place_id, PlaceName.language == language
        )
        res = await session.scalars(query)
        try:
            return res.one().name
        except exc.NoResultFound:
            _, _, place_name = get_place(user.place_id, language)
            place = PlaceName(
                place_id=user.place_id, language=language, name=place_name
            )
            session.add(place)
            await session.commit()
            return place_name
