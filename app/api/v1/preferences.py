from fastapi import APIRouter, HTTPException
from sqlalchemy import exc
from sqlalchemy.exc import NoResultFound

from app.api.dependencies import CurrentActiveUserDep, DbDep
from app.models.user import Preferences
from app.schemas.preferences import PreferencesInSchema, PreferencesOutSchema
from app.services.preferences import (
    create_user_preferences,
    get_user_preferences,
    update_user_preferences,
)

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferencesOutSchema)
async def get_preferences(db: DbDep, current_user: CurrentActiveUserDep) -> Preferences:
    """Fetch user preferences."""
    try:
        return await get_user_preferences(db, current_user.id)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Preferences not found") from e


@router.post("", response_model=PreferencesOutSchema)
async def create_preferences(
    db: DbDep,
    current_user: CurrentActiveUserDep,
    preferences_data: PreferencesInSchema,
) -> Preferences:
    """Create user preferences."""
    try:
        return await create_user_preferences(db, current_user.id, preferences_data)
    except exc.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Preferences already exist") from e


@router.put("", response_model=PreferencesOutSchema)
async def update_preferences(
    db: DbDep,
    current_user: CurrentActiveUserDep,
    preferences_data: PreferencesInSchema,
) -> Preferences:
    """Update user preferences."""
    try:
        return await update_user_preferences(
            db,
            current_user.id,
            preferences_data,
        )
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Preferences not found") from e
