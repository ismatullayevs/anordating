from sqlalchemy import and_, exists, select
from sqlalchemy.orm import selectinload, joinedload, aliased
from app.enums import FileTypes, ReactionType
from app.models.user import Reaction, User
from app.dto.user import UserRelMediaDTO
from aiogram.utils.media_group import MediaGroupBuilder
from math import radians, sin, cos, sqrt, atan2
from app.core.db import session_factory


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance


async def get_user(id: int | None = None, telegram_id: int | None = None, with_media=False, with_preferences=False):
    if not id and not telegram_id:
        raise ValueError("id or telegram_id must be provided")

    async with session_factory() as session:
        query = select(User)
        if id:
            query = query.where(User.id == id)
        else:
            query = query.where(User.telegram_id == telegram_id)

        if with_media:
            query = query.options(selectinload(User.media))
        if with_preferences:
            query = query.options(joinedload(User.preferences))

        res = await session.scalars(query)
        return res.one()


async def get_profile_card(user: User):
    async with session_factory() as session:
        session.add(user)
        await user.awaitable_attrs.media

    user_dto = UserRelMediaDTO.model_validate(user, from_attributes=True)
    caption = ", ".join(
        v for v in [user_dto.name, str(user_dto.age), user_dto.bio] if v)
    album_builder = MediaGroupBuilder(
        caption=caption
    )
    for media in user_dto.media:
        if media.file_type == FileTypes.image:
            album_builder.add_photo(media.telegram_id or media.path or '')
        elif media.file_type == FileTypes.video:
            album_builder.add_video(media.telegram_id or media.path or '')

    return album_builder.build()


async def get_likes(user: User):
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

        res = await session.scalars(query)
        return res.all()
