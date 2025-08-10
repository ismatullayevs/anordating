from fastapi import APIRouter, HTTPException

from app.api.dependencies import DbDep, VerifiedTokenDep
from app.models.user import User
from app.schemas.user import UserInSchema, UserOutSchema
from app.services.user import register_user

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserOutSchema)
async def register(
    db: DbDep,
    internal_token: VerifiedTokenDep,
    user_data: UserInSchema,
) -> User:
    """Register a new user."""
    if not internal_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await register_user(db, user_data)
