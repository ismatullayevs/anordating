from typing import Annotated

from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy import select

from api.dependencies import validate_init_data, validate_websocket_init_data
from api.websocket import handle_websocket
from shared.core.db import session_factory
from shared.dto.chat import ChatDTO, ChatInDTO, ChatMemberDTO, MessageDTO
from shared.models.chat import Chat, ChatMember, Message
from shared.queries import can_write, get_chat_by_users, get_user, select_chat_members

router = APIRouter()


@router.get("/chats", response_model=list[ChatDTO])
async def get_chats(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)
    async with session_factory() as session:
        query = select(Chat).join(ChatMember).where(ChatMember.user_id == user.id)
        res = await session.scalars(query)
        chats = res.all()
        return chats


@router.post("/chats", response_model=ChatDTO)
async def create_chat(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    chat: ChatInDTO,
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)
    match = await get_user(id=chat.match_id)
    async with session_factory() as session:
        if not await can_write(session, user.id, match.id):
            raise HTTPException(status_code=403, detail="You are not a match")

        chat_db = await get_chat_by_users(session, user.id, match.id)
        if chat_db:
            raise HTTPException(status_code=400, detail="Chat already exists")

        chat_db = Chat()
        chat_member1 = ChatMember(chat=chat_db, user_id=user.id)
        chat_member2 = ChatMember(chat=chat_db, user_id=match.id)

        session.add(chat_db)
        session.add(chat_member1)
        session.add(chat_member2)
        await session.commit()
        return chat_db


@router.delete("/chats/{chat_id}")
async def delete_chat(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    chat_id: int,
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)
    async with session_factory() as session:
        member = select(Chat).join(ChatMember).where(
            Chat.id == chat_id, ChatMember.user_id == user.id, ChatMember.chat_id == chat_id
        )
        res = await session.scalars(member)
        chat = res.one_or_none()
        if not chat:
            raise HTTPException(status_code=403, detail="You are not a member of this chat")
        
        await session.delete(chat)
        await session.commit()
        return {"detail": "Chat deleted"}


@router.get("/chats/{chat_id}/messages", response_model=list[MessageDTO])
async def get_messages(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    chat_id: int,
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)
    async with session_factory() as session:
        query = select(ChatMember).where(
            ChatMember.chat_id == chat_id, ChatMember.user_id == user.id
        )
        res = await session.scalars(query)
        member = res.one_or_none()
        if not member:
            raise HTTPException(
                status_code=403, detail="You are not a member of this chat"
            )

        query = select(Message).where(Message.chat_id == chat_id)
        res = await session.scalars(query)
        messages = res.all()
        return messages


@router.get("/chats/{chat_id}/members", response_model=list[ChatMemberDTO])
async def get_chat_members(
    init_data: Annotated[WebAppInitData, Depends(validate_init_data)],
    chat_id: int,
):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)
    async with session_factory() as session:
        members = await select_chat_members(session, chat_id=chat_id)
        return members


@router.websocket("/ws")
async def websocket_chats(
    websocket: WebSocket,
    init_data: Annotated[WebAppInitData, Depends(validate_websocket_init_data)],
):
    await handle_websocket(websocket, init_data)
