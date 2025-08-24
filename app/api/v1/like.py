from collections.abc import Sequence

from fastapi import APIRouter

from app.api.dependencies import CurrentActiveUserDep, DbDep
from app.models.user import User
from app.queries import get_likes
from app.schemas.user import UserOutSchema

router = APIRouter(prefix="/likes")


@router.get("", response_model=list[UserOutSchema])
async def get_user_likes(
    db: DbDep,
    current_user: CurrentActiveUserDep,
    limit: int = 10,
) -> Sequence[User]:
    """Get users who liked the given user."""
    return await get_likes(db, current_user.id, limit)
