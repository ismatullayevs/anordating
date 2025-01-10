from app.models.user import Preferences, User, Reaction
from sqlalchemy import select, and_, not_, exists, or_
from app.core.db import session_factory
from sqlalchemy.orm import joinedload


async def calculate_similarity(user1: User, user2: User):
    pass


async def get_best_match(id: int):
    async with session_factory() as session:
        query = select(User).where(User.id == id).options(joinedload(User.preferences))
        res = await session.scalars(query)
        current_user = res.one()

        query = select(User).join(Preferences).where(
            User.id != id,
            User.is_active == True,

            ~exists().where(and_(
                Reaction.from_user_id == current_user.id,
                Reaction.to_user_id == User.id
            )),
            
            ~exists().where(and_(
                Reaction.from_user_id == User.id,
                Reaction.to_user_id == current_user.id
            ))
        )

        if current_user.preferences.min_age and current_user.preferences.max_age:
            query = query.where(
                User.age >= current_user.preferences.min_age,
                User.age <= current_user.preferences.max_age,
            )

        if current_user.preferences.preferred_gender == "friends":
            query = query.where(
                Preferences.preferred_gender == "friends"
            )
        else:
            query = query.where(
                User.gender == current_user.preferences.preferred_gender,
                Preferences.preferred_gender == current_user.gender,
            )
        
        res = await session.scalars(query)
        potential_matches = res.all()
        if not potential_matches:
            return None
        return potential_matches[0].id
