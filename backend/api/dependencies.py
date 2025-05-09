from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import Header, HTTPException, WebSocket, WebSocketException

from shared.core.config import settings


async def validate_init_data(authorization: str | None = Header(None)):
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
