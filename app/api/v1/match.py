from fastapi import APIRouter

from app.api.dependencies import CurrentActiveUserDep, DbDep
from app.models.user import User
from app.schemas.user import UserOutSchema
from app.services.match import get_matches

router = APIRouter(prefix="/matches")


@router.get("", response_model=list[UserOutSchema])
async def fetch_matches(
    current_user: CurrentActiveUserDep,
    db: DbDep,
    limit: int = 10,
    offset: int = 0,
) -> list[User]:
    """Fetch a list of matches for the current user."""
    return await get_matches(current_user.id, db, limit, offset)
