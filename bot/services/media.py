from uuid import UUID

import httpx

from app.core.config import settings
from bot.schemas.media import FileSchema


async def get_media(user_id: UUID) -> list[FileSchema]:
    """Fetch matches for a user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/v1/media",
            params={"user_id": str(user_id)},
        )
        response.raise_for_status()
        return [FileSchema(**file) for file in response.json()]
