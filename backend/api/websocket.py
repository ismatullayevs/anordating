import json
from collections import defaultdict

from aiogram.utils.web_app import WebAppInitData
from fastapi import WebSocket

from shared.core.db import session_factory
from shared.dto.chat import MessageAddDTO
from shared.models.chat import Chat, ChatMember
from shared.queries import can_write, get_chat_by_users, get_user, select_chat_members


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


manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket, init_data: WebAppInitData):
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
                        session, chat_id=message_in["chat_id"]
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

                await manager.send_message(str(match_id), json.dumps(ws_message, default=str))
                await manager.send_message(str(user.id), json.dumps(ws_message, default=str))

    finally:
        await manager.disconnect(str(user.id), websocket)
