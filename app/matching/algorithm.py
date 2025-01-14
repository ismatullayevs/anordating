from dataclasses import dataclass
from app.models.user import Preferences, Report, User, Reaction
from sqlalchemy import select, and_, exists
from app.core.db import session_factory
from sqlalchemy.orm import joinedload
from app.utils import haversine_distance


async def get_potential_matches(current_user: User):
    async with session_factory() as session:
        session.add(current_user)
        await current_user.awaitable_attrs.preferences

        query = select(User).join(Preferences).where(
            User.id != current_user.id,
            User.is_active == True,

            ~exists().where(and_(
                Reaction.from_user_id == current_user.id,
                Reaction.to_user_id == User.id
            )),

            ~exists().where(and_(
                Reaction.from_user_id == User.id,
                Reaction.to_user_id == current_user.id
            )),

            ~exists().where(and_(
                Report.from_user_id == current_user.id,
                Report.to_user_id == User.id
            )),

            ~exists().where(and_(
                Report.from_user_id == User.id,
                Report.to_user_id == current_user.id
            )),
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
        return potential_matches


def calculate_age_similarity(age1: int, age2: int):
    max_age_diff = 10
    age_diff = abs(age1 - age2)
    age_score = max(0, 1 - (age_diff / max_age_diff))

    return age_score


def calculate_location_similarity(lat1, lon1, lat2, lon2):
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    max_distance = 50
    location_score = max(0, 1 - (distance / max_distance))

    return location_score


async def calculate_similarity(current_user: User, potential_match: User) -> float:
    async with session_factory() as session:
        session.add(current_user)
        await current_user.awaitable_attrs.preferences

    @dataclass
    class SimilarityWeights:
        location = 0.6
        age = 0.4

    total_score, total_weight = 0, 0

    total_score += calculate_location_similarity(
        current_user.latitude, current_user.longitude, potential_match.latitude,
        potential_match.longitude) * SimilarityWeights.location
    total_weight += SimilarityWeights.location

    if not current_user.preferences.min_age:
        total_score += calculate_age_similarity(
            current_user.age, potential_match.age) * SimilarityWeights.age
        total_weight += SimilarityWeights.age

    if total_weight == 0:
        return 0

    final_score = total_score / total_weight
    return round(final_score, 2)


async def get_best_match(current_user: User):
    async with session_factory() as session:
        session.add(current_user)
        await current_user.awaitable_attrs.preferences

    potential_matches = await get_potential_matches(current_user)
    best_match, best_similarity = None, 0
    for match in potential_matches:
        similarity = await calculate_similarity(current_user, match)
        if similarity > best_similarity:
            best_match = match
            best_similarity = similarity

    print(f"Best match: {best_match}, similarity: {best_similarity}")
    return best_match
