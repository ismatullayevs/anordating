from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_ban_success(superuser_client: AsyncClient):
    """Test successful ban creation by superuser."""
    ban_data = {
        "user_telegram_id": 999888777,
        "reason": "Spam and harassment",
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
    }

    response = await superuser_client.post("/v1/bans", json=ban_data)

    assert response.status_code == 200
    data = response.json()
    assert data["user_telegram_id"] == ban_data["user_telegram_id"]
    assert data["reason"] == ban_data["reason"]
    assert "id" in data
    assert "created_at" in data
    assert "expires_at" in data


@pytest.mark.asyncio
async def test_create_ban_permanent(superuser_client: AsyncClient):
    """Test creating a permanent ban (no expiration)."""
    ban_data = {
        "user_telegram_id": 888777666,
        "reason": "Permanent ban for severe violations",
    }

    response = await superuser_client.post("/v1/bans", json=ban_data)

    assert response.status_code == 200
    data = response.json()
    assert data["user_telegram_id"] == ban_data["user_telegram_id"]
    assert data["reason"] == ban_data["reason"]
    assert data["expires_at"] is None


@pytest.mark.asyncio
async def test_create_ban_non_superuser(authenticated_client: AsyncClient):
    """Test ban creation by non-superuser (should fail)."""
    ban_data = {
        "user_telegram_id": 777666555,
        "reason": "Should not be allowed",
    }

    response = await authenticated_client.post("/v1/bans", json=ban_data)

    assert response.status_code == 403
    assert "Only superusers can create bans" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_duplicate_ban(superuser_client: AsyncClient, test_ban):
    """Test creating duplicate active ban (should fail)."""
    ban_data = {
        "user_telegram_id": test_ban.user_telegram_id,
        "reason": "Duplicate ban attempt",
    }

    response = await superuser_client.post("/v1/bans", json=ban_data)

    assert response.status_code == 400
    assert "Active ban already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_bans_success(superuser_client: AsyncClient, test_ban):
    """Test getting bans list by superuser."""
    response = await superuser_client.get("/v1/bans")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check if test_ban is in the response
    ban_ids = [ban["id"] for ban in data]
    assert test_ban.id in ban_ids


@pytest.mark.asyncio
async def test_get_bans_with_filters(superuser_client: AsyncClient, test_ban):
    """Test getting bans with filters."""
    # Test filtering by user_telegram_id
    response = await superuser_client.get(f"/v1/bans?user_telegram_id={test_ban.user_telegram_id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(ban["user_telegram_id"] == test_ban.user_telegram_id for ban in data)

    # Test filtering by active_only
    response = await superuser_client.get("/v1/bans?active_only=true")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_bans_non_superuser(authenticated_client: AsyncClient):
    """Test getting bans by non-superuser (should fail)."""
    response = await authenticated_client.get("/v1/bans")

    assert response.status_code == 403
    assert "Only superusers can view bans" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_ban_by_id_success(superuser_client: AsyncClient, test_ban):
    """Test getting specific ban by ID."""
    response = await superuser_client.get(f"/v1/bans/{test_ban.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_ban.id
    assert data["user_telegram_id"] == test_ban.user_telegram_id
    assert data["reason"] == test_ban.reason


@pytest.mark.asyncio
async def test_get_ban_by_id_not_found(superuser_client: AsyncClient):
    """Test getting non-existent ban."""
    response = await superuser_client.get("/v1/bans/99999")

    assert response.status_code == 404
    assert "Ban not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_ban_by_id_non_superuser(authenticated_client: AsyncClient, test_ban):
    """Test getting ban by ID as non-superuser (should fail)."""
    response = await authenticated_client.get(f"/v1/bans/{test_ban.id}")

    assert response.status_code == 403
    assert "Only superusers can view bans" in response.json()["detail"]


@pytest.mark.asyncio
async def test_check_user_ban_status_banned(superuser_client: AsyncClient, test_ban):
    """Test checking ban status for banned user."""
    response = await superuser_client.get(f"/v1/bans/check/{test_ban.user_telegram_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == test_ban.user_telegram_id
    assert data["is_banned"] is True
    assert data["active_ban"] is not None
    assert data["active_ban"]["id"] == test_ban.id


@pytest.mark.asyncio
async def test_check_user_ban_status_not_banned(superuser_client: AsyncClient):
    """Test checking ban status for non-banned user."""
    response = await superuser_client.get("/v1/bans/check/123456789")

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == 123456789
    assert data["is_banned"] is False
    assert data["active_ban"] is None


@pytest.mark.asyncio
async def test_check_user_ban_status_non_superuser(authenticated_client: AsyncClient):
    """Test checking ban status as non-superuser (should fail)."""
    response = await authenticated_client.get("/v1/bans/check/123456789")

    assert response.status_code == 403
    assert "Only superusers can check ban status" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_ban_success(superuser_client: AsyncClient, test_ban):
    """Test updating ban by superuser."""
    update_data = {
        "reason": "Updated ban reason",
        "expires_at": (datetime.utcnow() + timedelta(days=14)).isoformat() + "Z",
    }

    response = await superuser_client.patch(f"/v1/bans/{test_ban.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["reason"] == update_data["reason"]
    assert data["id"] == test_ban.id


@pytest.mark.asyncio
async def test_update_ban_not_found(superuser_client: AsyncClient):
    """Test updating non-existent ban."""
    update_data = {
        "reason": "Updated reason",
    }

    response = await superuser_client.patch("/v1/bans/99999", json=update_data)

    assert response.status_code == 404
    assert "Ban not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_ban_non_superuser(authenticated_client: AsyncClient, test_ban):
    """Test updating ban as non-superuser (should fail)."""
    update_data = {
        "reason": "Should not be allowed",
    }

    response = await authenticated_client.patch(f"/v1/bans/{test_ban.id}", json=update_data)

    assert response.status_code == 403
    assert "Only superusers can update bans" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_ban_success(superuser_client: AsyncClient, test_ban):
    """Test deleting ban (unbanning user) by superuser."""
    response = await superuser_client.delete(f"/v1/bans/{test_ban.id}")

    assert response.status_code == 200
    data = response.json()
    assert "unbanned" in data["detail"].lower()

    # Verify ban is deleted
    get_response = await superuser_client.get(f"/v1/bans/{test_ban.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_ban_not_found(superuser_client: AsyncClient):
    """Test deleting non-existent ban."""
    response = await superuser_client.delete("/v1/bans/99999")

    assert response.status_code == 404
    assert "Ban not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_ban_non_superuser(authenticated_client: AsyncClient, test_ban):
    """Test deleting ban as non-superuser (should fail)."""
    response = await authenticated_client.delete(f"/v1/bans/{test_ban.id}")

    assert response.status_code == 403
    assert "Only superusers can delete bans" in response.json()["detail"]
