from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.i18n import gettext as _
from app.enums import FileTypes
from app.models.user import User
from app.core.db import session_factory
from math import ceil, radians, sin, cos, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance


async def get_profile_card(user: User, dist: float | None = None):
    assert user.is_active
    if dist:
        dist = ceil(dist)
        if dist > 15:
            dist = None
    
    dist_str = _("📍 {dist} km").format(dist=dist) if dist else None

    async with session_factory() as session:
        session.add(user)
        await user.awaitable_attrs.media

    caption = ", ".join(
        str(v) for v in [user.name, user.age, dist_str, user.bio] if v
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


async def clear_state(state: FSMContext, except_locale=False):
    data = {}
    if except_locale:
        locale = await state.get_value("locale")
        data["locale"] = locale
    await state.set_data(data)
