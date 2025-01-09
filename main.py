import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.handlers.registration import router as registration_router
from app.handlers.menu import router as menu_router
from app.middlewares import i18n_middleware
from redis.asyncio.client import Redis
from aiogram.fsm.storage.redis import RedisStorage


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
redis = Redis(host='redis', password=settings.REDIS_PASSWORD)
redis_storage = RedisStorage(redis)
dp = Dispatcher(storage=redis_storage)

i18n_middleware.setup(dp)

dp.include_router(registration_router)
dp.include_router(menu_router)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
