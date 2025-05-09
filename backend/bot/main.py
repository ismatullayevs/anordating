import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.types import MenuButtonWebApp, WebAppInfo
from motor.motor_asyncio import AsyncIOMotorClient

from bot.bot_commands import set_bot_profile
from bot.handlers.default import router as default_router
from bot.handlers.likes import router as likes_router
from bot.handlers.matches import router as matches_router
from bot.handlers.menu import router as menu_router
from bot.handlers.profile import router as profile_router
from bot.handlers.registration import router as registration_router
from bot.handlers.search import router as search_router
from bot.handlers.test import router as test_router
from bot.middlewares import i18n_middleware
from shared.core.config import EnvironmentTypes, settings
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    if settings.ENVIRONMENT == EnvironmentTypes.testing:
        session = AiohttpSession(api=TEST)
        bot = Bot(token=settings.BOT_TOKEN, session=session)

    await set_bot_profile(bot)
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="App", web_app=WebAppInfo(url="https://3135-82-215-85-234.ngrok-free.app")))

    mongo = AsyncIOMotorClient(
        host=settings.mongo_url,
        uuidRepresentation="standard",
    )
    mongo_storage = MongoStorage(mongo)
    dp = Dispatcher(storage=mongo_storage)

    i18n_middleware.setup(dp)

    dp.include_router(registration_router)
    dp.include_router(menu_router)
    dp.include_router(search_router)
    dp.include_router(likes_router)
    dp.include_router(profile_router)
    dp.include_router(matches_router)
    dp.include_router(default_router)

    if settings.DEBUG:
        dp.include_router(test_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
