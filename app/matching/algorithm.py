import logging
import time
from dataclasses import dataclass
from functools import lru_cache

from sqlalchemy import and_, exists, func, or_, select

from app.core.db import session_factory
from app.enums import PreferredGenders, ReactionType
from app.models.user import Ban, Preferences, Reaction, Report, User
from bot.utils import haversine_distance

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1000)
def calculate_location_similarity(lat1, lon1, lat2, lon2):
    """Cached version of location similarity calculation"""
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    max_distance = 50
    location_score = max(0, 1 - (distance / max_distance))
    return location_score


@lru_cache(maxsize=500)
def calculate_age_similarity(age1: int, age2: int):
    """Cached version of age similarity calculation"""
    max_age_diff = 10
    age_diff = abs(age1 - age2)
    age_score = max(0, 1 - (age_diff / max_age_diff))
    return age_score


async def get_potential_matches_batch(
    current_user: User, limit: int = 50, offset: int = 0
):
    """Get potential matches in batches for better performance"""
    assert current_user.is_active

    async with session_factory() as session:
        session.add(current_user)
        await current_user.awaitable_attrs.preferences

        query = (
            select(User)
            .join(Preferences)
            .where(
                User.id != current_user.id,
                User.is_active,
                or_(
                    Preferences.preferred_gender == current_user.gender,
                    Preferences.preferred_gender == PreferredGenders.both,
                ),
                ~exists().where(
                    and_(
                        Reaction.from_user_id == current_user.id,
                        Reaction.to_user_id == User.id,
                    )
                ),
                ~exists().where(
                    and_(
                        Reaction.from_user_id == User.id,
                        Reaction.to_user_id == current_user.id,
                        Reaction.reaction_type == ReactionType.dislike,
                    )
                ),
                ~exists().where(
                    and_(
                        Report.from_user_id == current_user.id,
                        Report.to_user_id == User.id,
                    )
                ),
                ~exists().where(
                    and_(
                        Report.from_user_id == User.id,
                        Report.to_user_id == current_user.id,
                    )
                ),
                ~exists().where(
                    and_(
                        Ban.user_telegram_id == User.telegram_id,
                        or_(Ban.expires_at == None, Ban.expires_at > func.now()),
                    )
                ),
            )
            .order_by(User.rating.desc())
            .limit(limit)
            .offset(offset)
        )

        min_age, max_age = (
            current_user.preferences.min_age,
            current_user.preferences.max_age,
        )
        if min_age and max_age:
            query = query.where(User.age.between(min_age, max_age))

        if not current_user.preferences.preferred_gender == PreferredGenders.both:
            query = query.where(
                User.gender == current_user.preferences.preferred_gender,
            )

        res = await session.scalars(query)
        potential_matches = res.all()
        return potential_matches


async def calculate_similarity(current_user: User, potential_match: User) -> float:
    @dataclass
    class SimilarityWeights:
        location = 0.6
        age = 0.4

    total_score, total_weight = 0, 0

    total_score += (
        calculate_location_similarity(
            current_user.latitude,
            current_user.longitude,
            potential_match.latitude,
            potential_match.longitude,
        )
        * SimilarityWeights.location
    )
    total_weight += SimilarityWeights.location

    if not current_user.preferences.min_age:
        total_score += (
            calculate_age_similarity(current_user.age, potential_match.age)
            * SimilarityWeights.age
        )
        total_weight += SimilarityWeights.age

    if total_weight == 0:
        return 0

    final_score = total_score / total_weight
    return round(final_score, 2)


async def calculate_total_score(user1: User, user2: User) -> float:
    """
    Calculate total score combining similarity and Elo rating.
    Returns a score between 0 and 1.

    Args:
        user1: First user
        user2: Second user
        weights: Optional custom weights for different factors

    Returns:
        float: Combined score between 0 and 1
    """

    @dataclass
    class ScoreWeights:
        similarity = 0.6
        rating = 0.4

    similarity_score = await calculate_similarity(user1, user2)

    rating_range = 800
    normalized_rating = (user2.rating - 1000) / rating_range
    normalized_rating = max(0, min(1, normalized_rating))

    total_score = (
        similarity_score * ScoreWeights.similarity
        + normalized_rating * ScoreWeights.rating
    )

    return round(total_score, 3)


async def get_best_match(current_user: User):
    start_time = time.time()

    async with session_factory() as session:
        session.add(current_user)
        await current_user.awaitable_attrs.preferences

    batch_size = 50
    offset = 0
    best_match, best_score = None, 0
    total_checked = 0

    while True:
        batch_start = time.time()
        potential_matches = await get_potential_matches_batch(
            current_user, limit=batch_size, offset=offset
        )
        batch_time = time.time() - batch_start

        if not potential_matches:
            break

        score_start = time.time()
        for match in potential_matches:
            score = await calculate_total_score(current_user, match)
            total_checked += 1
            if score > best_score:
                best_match = match
                best_score = score
        score_time = time.time() - score_start

        logger.debug(
            f"Batch {offset//batch_size + 1}: {len(potential_matches)} matches, "
            f"query_time={batch_time:.3f}s, score_time={score_time:.3f}s"
        )

        if best_score > 0.7:
            break

        offset += batch_size

        if offset >= 500:
            break

    total_time = time.time() - start_time
    logger.info(
        f"Matching completed: checked {total_checked} users, "
        f"best_score={best_score:.3f}, total_time={total_time:.3f}s"
    )

    return best_match
