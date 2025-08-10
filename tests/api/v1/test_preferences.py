import pytest
from httpx import AsyncClient

from app.enums import PreferredGenders


@pytest.mark.asyncio
async def test_get_preferences_success(client: AsyncClient, test_user, session):
    """Test getting user preferences."""
    # First create preferences for the user
    from app.models.user import Preferences
    
    prefs = Preferences(
        user_id=test_user.id,
        min_age=18,
        max_age=35,
        preferred_gender=PreferredGenders.both
    )
    session.add(prefs)
    await session.commit()
    await session.refresh(prefs)
    
    response = await client.get(f"/v1/preferences?user_id={test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["min_age"] == 18
    assert data["max_age"] == 35
    assert data["preferred_gender"] == PreferredGenders.both.value
    assert "id" in data


@pytest.mark.asyncio
async def test_get_preferences_not_found(client: AsyncClient, test_user):
    """Test getting preferences for user with no preferences."""
    response = await client.get(f"/v1/preferences?user_id={test_user.id}")
    
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_preferences_success(client: AsyncClient, test_user):
    """Test creating user preferences."""
    preferences_data = {
        "min_age": 20,
        "max_age": 30,
        "preferred_gender": PreferredGenders.female.value
    }
    
    response = await client.post(
        f"/v1/preferences?user_id={test_user.id}", 
        json=preferences_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["min_age"] == preferences_data["min_age"]
    assert data["max_age"] == preferences_data["max_age"]
    assert data["preferred_gender"] == preferences_data["preferred_gender"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_preferences_duplicate(client: AsyncClient, test_user, session):
    """Test creating preferences when they already exist."""
    # First create preferences for the user
    from app.models.user import Preferences
    
    prefs = Preferences(
        user_id=test_user.id,
        min_age=25,
        max_age=40,
        preferred_gender=PreferredGenders.male
    )
    session.add(prefs)
    await session.commit()
    
    preferences_data = {
        "min_age": 22,
        "max_age": 32,
        "preferred_gender": PreferredGenders.female.value
    }
    
    response = await client.post(
        f"/v1/preferences?user_id={test_user.id}", 
        json=preferences_data
    )
    
    assert response.status_code == 400
    assert "already exist" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_preferences_invalid_data(client: AsyncClient, test_user):
    """Test creating preferences with invalid data."""
    preferences_data = {
        "min_age": "invalid_age",
        "max_age": -5,
        "preferred_gender": "invalid_gender"
    }
    
    response = await client.post(
        f"/v1/preferences?user_id={test_user.id}", 
        json=preferences_data
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_preferences_missing_required_field(client: AsyncClient, test_user):
    """Test creating preferences without required field."""
    preferences_data = {
        "min_age": 20,
        "max_age": 30
        # Missing preferred_gender
    }
    
    response = await client.post(
        f"/v1/preferences?user_id={test_user.id}", 
        json=preferences_data
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_preferences_success(client: AsyncClient, test_user, session):
    """Test updating user preferences."""
    # First create preferences for the user
    from app.models.user import Preferences
    
    prefs = Preferences(
        user_id=test_user.id,
        min_age=18,
        max_age=35,
        preferred_gender=PreferredGenders.female
    )
    session.add(prefs)
    await session.commit()
    
    update_data = {
        "min_age": 21,
        "max_age": 28,
        "preferred_gender": PreferredGenders.both.value
    }
    
    response = await client.put(
        f"/v1/preferences?user_id={test_user.id}", 
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["min_age"] == update_data["min_age"]
    assert data["max_age"] == update_data["max_age"]
    assert data["preferred_gender"] == update_data["preferred_gender"]


@pytest.mark.asyncio
async def test_update_preferences_not_found(client: AsyncClient, test_user):
    """Test updating preferences that don't exist."""
    update_data = {
        "min_age": 21,
        "max_age": 28,
        "preferred_gender": PreferredGenders.both.value
    }
    
    response = await client.put(
        f"/v1/preferences?user_id={test_user.id}", 
        json=update_data
    )
    
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_preferences_invalid_data(client: AsyncClient, test_user, session):
    """Test updating preferences with invalid data."""
    # First create preferences
    from app.models.user import Preferences
    
    prefs = Preferences(
        user_id=test_user.id,
        min_age=18,
        max_age=35,
        preferred_gender=PreferredGenders.female
    )
    session.add(prefs)
    await session.commit()
    
    update_data = {
        "min_age": "not_a_number",
        "max_age": -10,
        "preferred_gender": "invalid_gender"
    }
    
    response = await client.put(
        f"/v1/preferences?user_id={test_user.id}", 
        json=update_data
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_preferences_with_null_ages(client: AsyncClient, test_user):
    """Test creating preferences with null min/max ages."""
    preferences_data = {
        "min_age": None,
        "max_age": None,
        "preferred_gender": PreferredGenders.both.value
    }
    
    response = await client.post(
        f"/v1/preferences?user_id={test_user.id}", 
        json=preferences_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["min_age"] is None
    assert data["max_age"] is None
    assert data["preferred_gender"] == preferences_data["preferred_gender"]


@pytest.mark.asyncio
async def test_preferences_invalid_user_id(client: AsyncClient):
    """Test preferences operations with invalid user ID."""
    preferences_data = {
        "min_age": 20,
        "max_age": 30,
        "preferred_gender": PreferredGenders.male.value
    }
    
    response = await client.post("/v1/preferences?user_id=invalid-uuid", json=preferences_data)
    assert response.status_code == 422  # Validation error
    
    response = await client.get("/v1/preferences?user_id=invalid-uuid")
    assert response.status_code == 422  # Validation error
    
    response = await client.put("/v1/preferences?user_id=invalid-uuid", json=preferences_data)
    assert response.status_code == 422  # Validation error
