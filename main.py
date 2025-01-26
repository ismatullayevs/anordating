import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.handlers.registration import router as registration_router
from app.handlers.menu import router as menu_router
from app.handlers.test import router as test_router
from app.handlers.likes import router as likes_router
from app.handlers.profile import router as profile_router
from app.handlers.search import router as search_router
from app.handlers.matches import router as matches_router
from app.middlewares import i18n_middleware
from redis.asyncio.client import Redis
from aiogram.fsm.storage.redis import RedisStorage


logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)
    redis_storage = RedisStorage(redis)
    dp = Dispatcher(storage=redis_storage)

    i18n_middleware.setup(dp)

    dp.include_router(registration_router)
    dp.include_router(search_router)
    dp.include_router(likes_router)
    dp.include_router(profile_router)
    dp.include_router(matches_router)
    dp.include_router(menu_router)

    if settings.DEBUG:
        dp.include_router(test_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

