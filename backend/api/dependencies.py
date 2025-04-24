from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import Header, HTTPException

from shared.core.config import settings


async def validate_init_data(authentication: str | None = Header(None)):
    if not authentication:
        raise HTTPException(status_code=401, detail="Authentication header missing")

    token_type, token = authentication.split(" ", 1)
    if token_type.lower() != "twa":
        raise HTTPException(status_code=401, detail="Invalid authentication format")

    try:
        init_data = safe_parse_webapp_init_data(
            token=settings.BOT_TOKEN, init_data=token
        )
        return init_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
