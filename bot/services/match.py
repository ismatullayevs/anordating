from uuid import UUID

import httpx

from app.core.config import settings
from bot.schemas.reaction import ReactionInSchema, ReactionSchema
from bot.schemas.user import UserSchema


async def get_matches(
    telegram_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[UserSchema]:
    """Fetch matches for a user."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Telegram-User-Id": str(telegram_id),
            "X-Internal-Token": settings.INTERNAL_TOKEN,
        }
        response = await client.get(
            f"{settings.API_URL}/v1/matches",
            params={"limit": limit, "offset": offset},
            headers=headers,
        )
        response.raise_for_status()
        return [UserSchema(**user) for user in response.json()]


async def get_best_match(
    telegram_id: int,
) -> UserSchema | None:
    """Fetch the best match for the current user."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Telegram-User-Id": str(telegram_id),
            "X-Internal-Token": settings.INTERNAL_TOKEN,
        }
        response = await client.get(
            f"{settings.API_URL}/v1/matches/find",
            headers=headers,
        )
        response.raise_for_status()
        return UserSchema(**response.json()) if response.json() else None


async def get_likes(
    telegram_id: int,
    limit: int,
) -> list[UserSchema]:
    """Fetch the likes for the current user."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Telegram-User-Id": str(telegram_id),
            "X-Internal-Token": settings.INTERNAL_TOKEN,
        }
        response = await client.get(
            f"{settings.API_URL}/v1/likes",
            headers=headers,
            params={"limit": limit},
        )
        response.raise_for_status()
        return [UserSchema(**user) for user in response.json()]


async def get_rewinds(
    telegram_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[UserSchema]:
    """Fetch the rewinds for the current user."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Telegram-User-Id": str(telegram_id),
            "X-Internal-Token": settings.INTERNAL_TOKEN,
        }
        response = await client.get(
            f"{settings.API_URL}/v1/rewinds",
            headers=headers,
            params={"limit": limit, "offset": offset},
        )
        response.raise_for_status()
        return [UserSchema(**user) for user in response.json()]


async def create_or_update_reaction(
    user_telegram_id: int,
    reaction_data: ReactionInSchema,
) -> ReactionSchema:
    """React to a user."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Telegram-User-Id": str(user_telegram_id),
            "X-Internal-Token": settings.INTERNAL_TOKEN,
        }
        response = await client.put(
            f"{settings.API_URL}/v1/reactions",
            headers=headers,
            json={
                "to_reaction_id": str(reaction_data.to_user_id),
                "reaction_type": reaction_data.reaction_type,
            },
        )
        response.raise_for_status()
        return ReactionSchema(**response.json())


async def check_match(user_telegram_id: int, match_id: UUID) -> bool:
    """Check if a match exists."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Telegram-User-Id": str(user_telegram_id),
            "X-Internal-Token": settings.INTERNAL_TOKEN,
        }
        response = await client.get(
            f"{settings.API_URL}/v1/matches/check",
            headers=headers,
            params={"match_id": str(match_id)},
        )
        response.raise_for_status()
        return response.json()["is_match"]
