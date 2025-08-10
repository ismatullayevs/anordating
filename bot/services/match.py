
import httpx

from app.core.config import settings
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
