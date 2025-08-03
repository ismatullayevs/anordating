from typing import Annotated

from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import Depends, Header, HTTPException, WebSocket, WebSocketException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import session_factory
from app.models.user import User
from app.services.user import get_user_by_telegram_id


async def get_db():
    async with session_factory() as session:
        yield session


DbDep = Annotated[AsyncSession, Depends(get_db)]


async def get_verified_internal_token(
    x_internal_token: Annotated[str | None, Header()],
):
    """
    Dependency to verify the internal token.
    """
    if x_internal_token is None:
        return
    if x_internal_token != settings.INTERNAL_TOKEN:
        raise HTTPException(
            status_code=401, detail="Unauthorized: Invalid internal token"
        )
    return x_internal_token


VerifiedTokenDep = Annotated[str, Depends(get_verified_internal_token)]


async def validate_init_data(authorization: Annotated[str | None, Header()] = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token_type, token = authorization.split(" ", 1)
    if token_type.lower() != "twa":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    try:
        init_data = safe_parse_webapp_init_data(
            token=settings.BOT_TOKEN, init_data=token
        )
        return init_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def validate_websocket_init_data(websocket: WebSocket):
    init_data = websocket.query_params.get("initData")
    if init_data is None:
        raise WebSocketException(401, "Authorization header missing")
    try:
        init_data = safe_parse_webapp_init_data(
            token=settings.BOT_TOKEN, init_data=init_data
        )
        return init_data
    except ValueError as e:
        raise WebSocketException(401, f"Invalid token: {str(e)}")


async def get_current_user(
    db: DbDep, init_data: Annotated[WebAppInitData, Depends(validate_init_data)]
):
    """Fetch the current user based on the provided init data."""
    if not init_data.user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        user = await get_user_by_telegram_id(db, init_data.user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return user


async def get_current_active_user(
    db: DbDep, init_data: Annotated[WebAppInitData, Depends(validate_init_data)]
):
    """Fetch the current active user based on the provided init data."""
    user = await get_current_user(db, init_data)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]
