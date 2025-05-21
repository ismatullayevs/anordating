import asyncio
import json
from collections import defaultdict
from aiogram import types

from aiogram.utils.web_app import WebAppInitData
from fastapi import BackgroundTasks, WebSocket, WebSocketDisconnect

from bot.utils import send_message
from shared.core.config import settings
from shared.core.db import session_factory
from shared.dto.chat import MessageAddDTO
from shared.models.chat import Chat, ChatMember
from shared.queries import can_write, get_chat_by_users, get_user, select_chat_members
from api.i18n import get_translator


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]
        await websocket.close()

    async def send_message(self, user_id: str, message: str):
        for connection in self.active_connections[user_id]:
            await connection.send_text(message)
    
    def is_connected(self, user_id: str) -> bool:
        return user_id in self.active_connections and bool(self.active_connections[user_id])


manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket, init_data: WebAppInitData, background_tasks: BackgroundTasks):
    assert init_data.user
    user = await get_user(telegram_id=init_data.user.id)
    if not user or not user.is_active:
        await websocket.close()
        return
    await manager.connect(str(user.id), websocket)
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            if data.get("type") == "new_message":
                message_in = data.get("payload")
                async with session_factory() as session:
                    members = await select_chat_members(
                        session, chat_id=message_in["chat_id"], with_user=True
                    )
                    if not user.id in [m.user_id for m in members]:
                        await manager.disconnect(str(user.id), websocket)
                        return
                    message = MessageAddDTO(**message_in, user_id=user.id)
                    message_orm = message.to_orm()
                    session.add(message_orm)
                    await session.commit()

                ws_message = {
                    "type": "new_message",
                    "payload": {
                        "id": message_orm.id,
                        "chat_id": message_orm.chat_id,
                        "user_id": message_orm.user_id,
                        "text": message_orm.text,
                        "created_at": message_orm.created_at.isoformat(),
                        "updated_at": message_orm.updated_at.isoformat(),
                    },
                }
                for member in members:
                    if not manager.is_connected(str(member.user_id)) and member.user_id != user.id:
                        _ = get_translator(member.user.ui_language.name)
                        mk = types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    types.InlineKeyboardButton(
                                        text=_("Open chat"),
                                        web_app=types.WebAppInfo(
                                            url=f"{settings.APP_URL}/users/{user.id}/chat"
                                        ),
                                    )
                                ],
                            ]
                        )
                        msg = _("You have a new message from {name}")
                        asyncio.ensure_future(
                            send_message(str(member.user.telegram_id), msg.format(name=user.name), reply_markup=mk)
                        )
                    await manager.send_message(
                        str(member.user_id), json.dumps(ws_message, default=str)
                    )

            elif data.get("type") == "new_chat":
                payload = data.get("payload")
                async with session_factory() as session:
                    match_id = payload["match_id"]
                    if not await can_write(session, user.id, match_id):
                        await manager.disconnect(str(user.id), websocket)
                        return

                    chat_db = await get_chat_by_users(session, user.id, match_id)
                    if chat_db:
                        await manager.disconnect(str(user.id), websocket)
                        return

                    chat_db = Chat()
                    chat_member1 = ChatMember(chat=chat_db, user=user)
                    chat_member2 = ChatMember(chat=chat_db, user_id=match_id)

                    session.add(chat_db)
                    await session.commit()

                ws_message = {
                    "type": "new_chat",
                    "payload": chat_db.__dict__,
                }

                await manager.send_message(
                    str(match_id), json.dumps(ws_message, default=str)
                )
                await manager.send_message(
                    str(user.id), json.dumps(ws_message, default=str)
                )

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        await manager.disconnect(str(user.id), websocket)
