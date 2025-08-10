import pytest
from httpx import AsyncClient

from app.schemas.user import UserInSchema
from bot.config import settings


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, test_user: UserInSchema) -> None:
    """Test successful user registration."""
    headers = {"X-Internal-Token": settings.INTERNAL_TOKEN}
    response = await client.post(
        "/v1/auth/register",
        json=test_user.model_dump(mode="json"),
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == test_user.telegram_id
    assert data["name"] == test_user.name
    assert data["bio"] == test_user.bio
    assert data["gender"] == test_user.gender
    assert data["ui_language"] == test_user.ui_language
    assert "id" in data
    assert "rating" in data
    assert data["is_active"] is True
