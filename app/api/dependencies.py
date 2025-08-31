from collections.abc import AsyncGenerator
from typing import Annotated

from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import Depends, Header, HTTPException, WebSocket, WebSocketException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import session_factory
from app.models.user import User
from app.services.user import get_user_by_telegram_id


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Get a database session."""
    async with session_factory() as session:
        yield session


DbDep = Annotated[AsyncSession, Depends(get_db)]


async def get_verified_internal_token_optional(
    x_internal_token: Annotated[str | None, Header()],
) -> str | None:
    """Verify and return the internal token if valid.

    Returns None if the token is missing or invalid.
    """
    if x_internal_token is None:
        return None
    if x_internal_token != settings.INTERNAL_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid internal token",
        )
    return x_internal_token


async def get_verified_internal_token(
    x_internal_token: Annotated[
        str | None,
        Depends(get_verified_internal_token_optional),
    ],
) -> str:
    """Dependency to verify the internal token.

    Raises HTTPException if the token is invalid or missing.
    """
    if x_internal_token is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing internal token",
        )
    return x_internal_token


VerifiedTokenDep = Annotated[str, Depends(get_verified_internal_token)]


async def validate_init_data_optional(
    authorization: Annotated[str | None, Header()] = None,
) -> WebAppInitData | None:
    """Dependency to validate the init data from the web app."""
    if not authorization:
        return None

    token_type, token = authorization.split(" ", 1)
    if token_type.lower() != "twa":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    try:
        return safe_parse_webapp_init_data(
            token=settings.BOT_TOKEN,
            init_data=token,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e!s}") from e


async def validate_init_data(
    init_data: Annotated[WebAppInitData | None, Depends(validate_init_data_optional)],
) -> WebAppInitData:
    """Dependency to validate the init data from the web app."""
    if not init_data:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return init_data


async def validate_websocket_init_data(websocket: WebSocket) -> WebAppInitData:
    """Dependency to validate the init data from the web app."""
    init_data = websocket.query_params.get("initData")
    if init_data is None:
        raise WebSocketException(401, "Authorization header missing")
    try:
        return safe_parse_webapp_init_data(
            token=settings.BOT_TOKEN,
            init_data=init_data,
        )
    except ValueError as e:
        raise WebSocketException(401, f"Invalid token: {e!s}") from e


async def get_current_user(
    db: DbDep,
    init_data: Annotated[
        WebAppInitData | None,
        Depends(validate_init_data_optional),
    ] = None,
    internal_token: Annotated[
        str | None,
        Depends(get_verified_internal_token_optional),
    ] = None,
    x_telegram_user_id: Annotated[str | None, Header()] = None,
) -> User:
    """Fetch the current user based on the provided init data."""
    if internal_token:
        if not x_telegram_user_id:
            raise HTTPException(status_code=401, detail="User ID header missing")
        try:
            user = await get_user_by_telegram_id(db, int(x_telegram_user_id))
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return user

    if not init_data:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not init_data.user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        user = await get_user_by_telegram_id(db, init_data.user.id)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_active_user(current_user: CurrentUserDep) -> User:
    """Fetch the current active user based on the provided init data."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    return current_user


CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]
