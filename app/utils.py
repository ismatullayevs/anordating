import math
from math import atan2, cos, radians, sin, sqrt

from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.media_group import MediaGroupBuilder

from app.core.db import session_factory
from app.enums import FileTypes
from app.models.user import User
from app.queries import get_city_name


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


async def get_profile_card(user: User, from_user: User | None = None):
    assert user.is_active
    caption = f"{user.name}, {user.age}"

    language = from_user.ui_language if from_user else user.ui_language
    city = await get_city_name(user, language)
    location_str = f"📍 {city}" if city else ""
    if from_user:
        dist = haversine_distance(
            user.latitude, user.longitude, from_user.latitude, from_user.longitude
        )
        if dist <= 20 and dist != 0:
            location_str = _("📍 {dist} km").format(dist=int(math.ceil(dist)))

    caption += f", {location_str}" if location_str else ""
    caption += f"\n\n{user.bio}" if user.bio else ""

    async with session_factory() as session:
        session.add(user)
        await user.awaitable_attrs.media

    album_builder = MediaGroupBuilder(caption=caption)
    for media in user.media:
        if media.file_type == FileTypes.image:
            album_builder.add_photo(media.telegram_id or media.path or "")
        elif media.file_type == FileTypes.video:
            album_builder.add_video(media.telegram_id or media.path or "")

    return album_builder.build()


async def clear_state(state: FSMContext, except_locale=False):
    data = {}
    if except_locale:
        locale = await state.get_value("locale")
        data["locale"] = locale
    await state.set_data(data)
