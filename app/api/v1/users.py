# TODO: change the file name to user.py
from operator import and_
from typing import Annotated
from uuid import UUID

from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import exc, exists, select

from app.api.dependencies import CurrentUserDep, DbDep, validate_init_data
from app.core.db import session_factory
from app.models.chat import Chat, ChatMember
from app.queries import get_user
from app.schemas.user import FileInSchema, FileOutSchema
from app.services.user import (
    add_user_media,
    batch_add_user_media,
    delete_user_media,
    get_user_media,
)

router = APIRouter()


@router.get("/users/me")
async def read_users_me(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id, is_active=True)
    return user


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
                and_(ChatMember.chat_id == Chat.id, ChatMember.user_id == match_id)
            ),
            exists().where(
                and_(ChatMember.chat_id == Chat.id, ChatMember.user_id == user.id)
            ),
        )
        res = await session.scalars(query)
        try:
            return res.one()
        except exc.NoResultFound:
            raise HTTPException(status_code=404, detail="Chat not found")


@router.get("/users/{user_id}/media", response_model=list[FileOutSchema])
async def get_media(db: DbDep, user_id: UUID):
    """Fetches media files associated with a user."""
    media = await get_user_media(db, user_id)
    return media


@router.post("/users/me/media", response_model=FileOutSchema)
async def add_media(db: DbDep, current_user: CurrentUserDep, file_data: FileInSchema):
    """Adds media files to a user."""
    try:
        file = await add_user_media(db, current_user.id, file_data)
        return file
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/me/media-batch", response_model=list[FileOutSchema])
async def batch_add_media(
    db: DbDep, current_user: CurrentUserDep, files_data: list[FileInSchema]
):
    """Adds multiple media files to a user."""
    if not files_data:
        raise HTTPException(status_code=400, detail="No files provided")

    try:
        files = await batch_add_user_media(db, current_user.id, files_data)
        return files
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/me/media/{file_id}")
async def delete_media(db: DbDep, current_user: CurrentUserDep, file_id: int):
    """Deletes a media file associated with a user."""
    try:
        await delete_user_media(db, current_user.id, file_id)
        return {"detail": "Media file deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
