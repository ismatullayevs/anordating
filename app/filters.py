from aiogram.filters import Filter
from aiogram.types import Message


class IsHumanUser(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        if not message.from_user or message.from_user.is_bot:
            return False
        return True
