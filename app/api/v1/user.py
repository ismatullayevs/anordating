# TODO: change the file name to user.py
from operator import and_
from typing import Annotated

from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import exc, exists, select

from app.api.dependencies import CurrentUserDep, DbDep, validate_init_data
from app.core.db import session_factory
from app.models.chat import Chat, ChatMember
from app.models.user import User
from app.queries import get_user
from app.schemas.user import UserOutSchema, UserUpdateSchema

router = APIRouter()


@router.get("/users/me", response_model=UserOutSchema)
async def read_users_me(
    current_user: CurrentUserDep,
) -> User:
    """Get current user."""
    return current_user


@router.put("/users/me")
async def update_current_user(
    db: DbDep,
    current_user: CurrentUserDep,
    user_update: UserUpdateSchema,
) -> dict[str, str]:
    """Update current user."""
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.add(current_user)
    await db.commit()
    return {"message": "User updated"}


@router.get("/users/{user_id}")
async def read_user(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    user_id: str,
):
    assert init_data.user
    try:
        user = await get_user(id=user_id, is_active=True)
        return user
    except exc.NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users/{match_id}/chat")
async def get_user_chat(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    match_id: str,
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id, is_active=True)
    try:
        match = await get_user(id=match_id, is_active=True)
    except exc.NoResultFound:
        raise HTTPException(status_code=404, detail="Match not found")

    async with session_factory() as session:
        query = select(Chat).where(
            exists().where(
                and_(ChatMember.chat_id == Chat.id, ChatMember.user_id == match_id),
            ),
            exists().where(
                and_(ChatMember.chat_id == Chat.id, ChatMember.user_id == user.id),
            ),
        )
        res = await session.scalars(query)
        try:
            return res.one()
        except exc.NoResultFound:
            raise HTTPException(status_code=404, detail="Chat not found")
