from operator import and_
from typing import Annotated

from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Depends
from sqlalchemy import exists, select

from api.dependencies import validate_init_data
from shared.core.db import session_factory
from shared.models.chat import Chat, ChatMember
from shared.queries import get_user

router = APIRouter()


@router.get("/users/me")
async def read_users_me(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)
    return user


@router.get("/users/{user_id}")
async def read_user(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    user_id: str,
):
    assert init_data.user
    user = await get_user(id=user_id)
    return user


@router.get("/users/{match_id}/chat")
async def get_user_chat(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    match_id: str,
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)

    async with session_factory() as session:
        query = select(Chat).where(
            exists().where(
                and_(ChatMember.chat_id == Chat.id, ChatMember.user_id == match_id)
            ),
            exists().where(
                and_(ChatMember.chat_id == Chat.id, ChatMember.user_id == user.id)
            ),
        )
        res = await session.scalars(query)
        return res.one_or_none()
