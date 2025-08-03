from fastapi import APIRouter, HTTPException

from app.api.dependencies import DbDep, VerifiedTokenDep
from app.schemas.user import UserInSchema, UserOutSchema
from app.services.user import register_user

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserOutSchema)
async def register(
    db: DbDep, verified_tg_token: VerifiedTokenDep, user_data: UserInSchema
):
    if not verified_tg_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = await register_user(db, user_data)
    return user
