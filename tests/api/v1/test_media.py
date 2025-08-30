import pytest
from httpx import AsyncClient

from app.enums import FileTypes


@pytest.mark.asyncio
async def test_get_media_success(authenticated_client: AsyncClient, test_user):
    """Test getting user media."""
    response = await authenticated_client.get(f"/v1/media?user_id={test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_add_media_success(authenticated_client: AsyncClient):
    """Test adding single media file."""
    file_data = {
        "telegram_id": "test_file_456",
        "telegram_unique_id": "unique_456",
        "file_type": FileTypes.image.value,
        "file_size": 2048,
        "mime_type": "image/png",
    }

    response = await authenticated_client.post("/v1/media", json=file_data)

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == file_data["telegram_id"]
    assert data["file_type"] == file_data["file_type"]
    assert data["file_size"] == file_data["file_size"]
    assert data["mime_type"] == file_data["mime_type"]
    assert "id" in data
    assert "uploaded_at" in data


@pytest.mark.asyncio
async def test_add_media_invalid_data(authenticated_client: AsyncClient):
    """Test adding media with invalid data."""
    file_data = {
        "telegram_id": "",
        "file_type": "invalid_type",
        "file_size": "invalid_size",
        "mime_type": None,
    }

    response = await authenticated_client.post("/v1/media", json=file_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_batch_add_media_success(authenticated_client: AsyncClient):
    """Test adding multiple media files."""
    files_data = [
        {
            "telegram_id": "batch_file_1",
            "telegram_unique_id": "batch_unique_1",
            "file_type": FileTypes.image.value,
            "file_size": 1024,
            "mime_type": "image/jpeg",
        },
        {
            "telegram_id": "batch_file_2",
            "telegram_unique_id": "batch_unique_2",
            "file_type": FileTypes.video.value,
            "file_size": 5120,
            "mime_type": "video/mp4",
        },
    ]

    response = await authenticated_client.post("/v1/media/batch-add", json=files_data)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["telegram_id"] == files_data[0]["telegram_id"]
    assert data[1]["telegram_id"] == files_data[1]["telegram_id"]


@pytest.mark.asyncio
async def test_batch_add_media_empty_list(authenticated_client: AsyncClient):
    """Test batch adding with empty files list."""
    response = await authenticated_client.post("/v1/media/batch-add", json=[])

    assert response.status_code == 400
    assert "No files provided" in response.json()["detail"]


@pytest.mark.asyncio
async def test_batch_add_media_invalid_data(authenticated_client: AsyncClient):
    """Test batch adding with invalid file data."""
    files_data = [
        {
            "telegram_id": "valid_file",
            "file_type": FileTypes.image.value,
            "file_size": 1024,
        },
        {
            "telegram_id": "invalid_file",
            "file_type": "invalid_type",
            "file_size": "invalid_size",
        },
    ]

    response = await authenticated_client.post("/v1/media/batch-add", json=files_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_delete_media_success(authenticated_client: AsyncClient, test_file):
    """Test deleting media file."""
    response = await authenticated_client.delete(f"/v1/media/{test_file.id}")

    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["detail"]


@pytest.mark.asyncio
async def test_delete_media_not_found(authenticated_client: AsyncClient):
    """Test deleting non-existent media file."""
    response = await authenticated_client.delete("/v1/media/99999")

    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_media_not_owned(authenticated_client: AsyncClient, session, test_user_2):
    """Test deleting media file not owned by current user."""
    # Create a file owned by test_user_2
    from app.models.file import File, UserMedia

    other_file = File(
        telegram_id="other_file_123",
        telegram_unique_id="other_unique_123",
        file_type=FileTypes.image.value,
        file_size=1024,
        mime_type="image/jpeg",
    )
    session.add(other_file)
    await session.flush()

    user_media = UserMedia(
        user_id=test_user_2.id,
        file_id=other_file.id,
    )
    session.add(user_media)
    await session.commit()
    await session.refresh(other_file)

    response = await authenticated_client.delete(f"/v1/media/{other_file.id}")

    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_media_with_thumbnail(authenticated_client: AsyncClient):
    """Test adding media with thumbnail."""
    file_data = {
        "telegram_id": "main_file_789",
        "telegram_unique_id": "main_unique_789",
        "file_type": FileTypes.video.value,
        "file_size": 10240,
        "mime_type": "video/mp4",
        "thumbnail": {
            "telegram_id": "thumb_file_789",
            "telegram_unique_id": "thumb_unique_789",
            "file_type": FileTypes.image.value,
            "file_size": 512,
            "mime_type": "image/jpeg",
        },
    }

    response = await authenticated_client.post("/v1/media", json=file_data)

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == file_data["telegram_id"]
    assert data["file_type"] == file_data["file_type"]
    assert data["thumbnail"] is not None
    assert data["thumbnail"]["telegram_id"] == file_data["thumbnail"]["telegram_id"]


@pytest.mark.asyncio
async def test_add_media_with_duration(authenticated_client: AsyncClient):
    """Test adding media with duration (for video/audio)."""
    file_data = {
        "telegram_id": "video_with_duration",
        "telegram_unique_id": "video_unique_duration",
        "file_type": FileTypes.video.value,
        "file_size": 15360,
        "mime_type": "video/mp4",
        "duration": 120,  # 2 minutes
    }

    response = await authenticated_client.post("/v1/media", json=file_data)

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == file_data["telegram_id"]
    assert data["duration"] == file_data["duration"]


@pytest.mark.asyncio
async def test_get_media_different_user(authenticated_client: AsyncClient, test_user_2):
    """Test getting media for different user."""
    response = await authenticated_client.get(f"/v1/media?user_id={test_user_2.id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # This should return media for test_user_2, not the authenticated user
