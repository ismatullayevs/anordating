from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencies import CurrentUserDep, DbDep
from app.schemas.ban import BanInSchema, BanOutSchema, BanUpdateSchema
from app.services.ban import (
    create_ban,
    get_bans,
    get_ban_by_id,
    get_active_ban_by_telegram_id,
    update_ban,
    delete_ban,
    is_user_banned,
)

router = APIRouter(prefix="/bans", tags=["bans"])


@router.post("", response_model=BanOutSchema)
async def create_user_ban(
    db: DbDep, current_user: CurrentUserDep, ban_data: BanInSchema
):
    """Creates a new ban. Only superusers can create bans."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can create bans")
    
    try:
        ban = await create_ban(db, ban_data)
        return ban
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[BanOutSchema])
async def get_user_bans(
    db: DbDep,
    current_user: CurrentUserDep,
    user_telegram_id: Optional[int] = Query(None, description="Filter by user telegram ID"),
    active_only: bool = Query(False, description="Show only active bans"),
    limit: int = Query(100, ge=1, le=1000, description="Number of bans to return"),
    offset: int = Query(0, ge=0, description="Number of bans to skip"),
):
    """Fetches bans. Only superusers can view bans."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can view bans")
    
    bans = await get_bans(
        db,
        user_telegram_id=user_telegram_id,
        active_only=active_only,
        limit=limit,
        offset=offset
    )
    return bans


@router.get("/{ban_id}", response_model=BanOutSchema)
async def get_ban(db: DbDep, current_user: CurrentUserDep, ban_id: int):
    """Fetches a specific ban by ID. Only superusers can view bans."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can view bans")
    
    ban = await get_ban_by_id(db, ban_id)
    if not ban:
        raise HTTPException(status_code=404, detail="Ban not found")
    
    return ban


@router.get("/check/{telegram_id}")
async def check_user_ban_status(
    db: DbDep, current_user: CurrentUserDep, telegram_id: int
):
    """Checks if a user is currently banned. Only superusers can check ban status."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can check ban status")
    
    is_banned = await is_user_banned(db, telegram_id)
    active_ban = None
    if is_banned:
        active_ban = await get_active_ban_by_telegram_id(db, telegram_id)
    
    return {
        "telegram_id": telegram_id,
        "is_banned": is_banned,
        "active_ban": active_ban
    }


@router.patch("/{ban_id}", response_model=BanOutSchema)
async def update_user_ban(
    db: DbDep, current_user: CurrentUserDep, ban_id: int, update_data: BanUpdateSchema
):
    """Updates a ban. Only superusers can update bans."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can update bans")
    
    try:
        ban = await update_ban(db, ban_id, update_data)
        return ban
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{ban_id}")
async def delete_user_ban(db: DbDep, current_user: CurrentUserDep, ban_id: int):
    """Deletes a ban (unbans the user). Only superusers can delete bans."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can delete bans")
    
    try:
        await delete_ban(db, ban_id)
        return {"detail": "Ban deleted successfully (user unbanned)"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
