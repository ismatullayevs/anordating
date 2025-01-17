from aiogram.utils.media_group import MediaGroupBuilder
from app.enums import FileTypes
from app.models.user import User
from app.core.db import session_factory
from math import radians, sin, cos, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance


async def get_profile_card(user: User):
    assert user.is_active
    async with session_factory() as session:
        session.add(user)
        await user.awaitable_attrs.media

    caption = ", ".join(
        v for v in [user.name, str(user.age), user.bio] if v
    )
    album_builder = MediaGroupBuilder(
        caption=caption
    )
    for media in user.media:
        if media.file_type == FileTypes.image:
            album_builder.add_photo(media.telegram_id or media.path or '')
        elif media.file_type == FileTypes.video:
            album_builder.add_video(media.telegram_id or media.path or '')

    return album_builder.build()
