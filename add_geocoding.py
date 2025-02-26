import asyncio

from sqlalchemy import select

from app.core.db import session_factory
from app.enums import UILanguages
from app.geocoding import get_place, get_place_id
from app.models.user import Place, PlaceName, User


async def update_users():
    async with session_factory() as session:
        query = select(User).where(User.place_id.is_(None), User.is_active.is_(True))
        result = await session.scalars(query)
        users = result.all()

        for user in users:
            place_id = get_place_id(user.latitude, user.longitude)
            if place_id:
                query = select(Place).where(Place.id == place_id)
                result = await session.scalars(query)
                place = result.one_or_none()
                if not place:
                    place = Place(id=place_id)
                    session.add(place)
                    place_name = get_place(place_id, language=UILanguages.en)[2]
                    placename = PlaceName(
                        place=place, language=UILanguages.en, name=place_name
                    )
                    session.add(placename)
                user.place = place

        await session.commit()


if __name__ == "__main__":
    asyncio.run(update_users())
