from aiogram.filters import Filter
from aiogram.types import Message
from app.queries import get_user


class IsHuman(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return False
        return {'from_user': message.from_user}


class IsBot(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message):
        return bool(message.from_user and message.from_user.is_bot)


class IsHumanUser(Filter):
    def __init__(self, with_media=False, with_preferences=False) -> None:
        self.with_media = with_media
        self.with_preferences = with_preferences

    async def __call__(self, message: Message):
        if not await IsHuman().__call__(message):
            return False

        user = await get_user(telegram_id=message.from_user.id,  # type: ignore
                              with_media=self.with_media,
                              with_preferences=self.with_preferences)
        return {'user': user}


class IsActiveHumanUser(Filter):
    def __init__(self, with_media=False, with_preferences=False) -> None:
        self.with_media = with_media
        self.with_preferences = with_preferences

    async def __call__(self, message: Message):
        result = await IsHumanUser(self.with_media, self.with_preferences).__call__(message)
        if not result:
            return False

        if not result["user"].is_active:
            return False

        return result


class IsInactiveHumanUser(Filter):
    def __init__(self, with_media=False, with_preferences=False) -> None:
        self.with_media = with_media
        self.with_preferences = with_preferences

    async def __call__(self, message: Message):
        result = await IsHumanUser(self.with_media, self.with_preferences).__call__(message)
        if not result:
            return False

        if result["user"].is_active:
            return False

        return {'user': result["user"]}
