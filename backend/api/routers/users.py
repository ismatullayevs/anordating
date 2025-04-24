from typing import Annotated

from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Depends

from api.dependencies import validate_init_data

router = APIRouter()


@router.get("/users/me")
async def read_users_me(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
):
    pass
