from uuid import UUID

import httpx

from bot.config import settings
from bot.schemas.user import UserSchema, UserUpdateSchema


async def get_user(user_id: UUID) -> UserSchema:
    """Get a user by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.API_URL}/v1/users/{user_id}")
        response.raise_for_status()
        return UserSchema(**response.json())


async def get_current_user(telegram_id: int) -> UserSchema:
    """Get the current user."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Telegram-User-Id": str(telegram_id),
            "X-Internal-Token": settings.INTERNAL_TOKEN,
        }
        response = await client.get(
            f"{settings.API_URL}/v1/users/me",
            headers=headers,
        )
        response.raise_for_status()
        return UserSchema(**response.json())


async def update_user(telegram_id: int, user_data: UserUpdateSchema) -> UserSchema:
    """Update user data."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Telegram-User-Id": str(telegram_id),
        }

        response = await client.put(
            f"{settings.API_URL}/v1/users/me",
            json=user_data.model_dump(exclude_unset=True, mode="json"),
            headers=headers,
        )
        response.raise_for_status()
        return UserSchema(**response.json())


async def delete_user(telegram_id: int) -> None:
    """Delete user."""
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Telegram-User-Id": str(telegram_id),
        }

        response = await client.delete(
            f"{settings.API_URL}/v1/users/me",
            headers=headers,
        )
        response.raise_for_status()
