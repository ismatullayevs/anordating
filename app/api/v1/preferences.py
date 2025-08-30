from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.dependencies import DbDep
from app.schemas.preferences import PreferencesInSchema, PreferencesOutSchema
from app.services.preferences import (
    create_user_preferences,
    get_user_preferences,
    update_user_preferences,
)

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferencesOutSchema)
async def get_preferences(db: DbDep, user_id: UUID):
    """Fetches user preferences."""
    try:
        preferences = await get_user_preferences(db, user_id)
        return preferences
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=PreferencesOutSchema)
async def create_preferences(
    db: DbDep,
    user_id: UUID,
    preferences_data: PreferencesInSchema,
):
    """Create user preferences."""
    try:
        return await create_user_preferences(db, user_id, preferences_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("", response_model=PreferencesOutSchema)
async def update_preferences(
    db: DbDep,
    user_id: UUID,
    preferences_data: PreferencesInSchema,
):
    """Update user preferences."""
    try:
        preferences = await update_user_preferences(db, user_id, preferences_data)
        for key, value in preferences_data.model_dump(exclude_unset=True).items():
            setattr(preferences, key, value)
        db.add(preferences)
        await db.commit()
        return preferences
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
