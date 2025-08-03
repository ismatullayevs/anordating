from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.dependencies import DbDep
from app.schemas.preferences import PreferencesOutSchema
from app.services.preferences import get_user_preferences

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferencesOutSchema)
async def get_preferences(db: DbDep, user_id: UUID):
    """Fetches user preferences."""
    try:
        preferences = await get_user_preferences(db, user_id)
        return preferences
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
