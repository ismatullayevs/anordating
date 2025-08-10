from uuid import UUID

import httpx

from bot.config import settings
from bot.schemas.report import ReportSchema


async def create_report(
    user_telegram_id: int,
    to_user_id: UUID,
    reason: str,
) -> ReportSchema:
    """Create a new report."""
    headers = {
        "X-Telegram-User-Id": str(user_telegram_id),
        "X-Internal-Token": settings.INTERNAL_TOKEN,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.API_URL}/v1/reports",
            headers=headers,
            json={"reason": reason, "to_user_id": str(to_user_id)},
        )
        response.raise_for_status()
        return ReportSchema(**response.json())
