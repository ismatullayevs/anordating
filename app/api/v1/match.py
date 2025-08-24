from collections.abc import Sequence

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentActiveUserDep, DbDep
from app.exceptions import RewindLimitExceededError
from app.matching.algorithm import get_best_match
from app.models.user import User
from app.schemas.user import UserOutSchema
from app.services.match import get_matches, get_rewinds

router = APIRouter()


@router.get("/matches", response_model=list[UserOutSchema])
async def fetch_matches(
    current_user: CurrentActiveUserDep,
    db: DbDep,
    limit: int = 10,
    offset: int = 0,
) -> list[User]:
    """Fetch a list of matches for the current user."""
    return await get_matches(current_user.id, db, limit, offset)


@router.get("/matches/find", response_model=UserOutSchema | None)
async def fetch_best_match(
    current_user: CurrentActiveUserDep,
    db: DbDep,
) -> User | None:
    """Fetch the best match for the current user."""
    return await get_best_match(current_user.id, db)


@router.get("/rewinds", response_model=list[UserOutSchema])
async def fetch_rewind_matches(
    current_user: CurrentActiveUserDep,
    db: DbDep,
    limit: int = 10,
    offset: int = 0,
) -> Sequence[User]:
    """List of rewinds for the current user."""
    try:
        return await get_rewinds(current_user.id, db, limit, offset)
    except RewindLimitExceededError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
