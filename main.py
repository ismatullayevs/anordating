import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.handlers.registration import router as registration_router
from app.middlewares import i18n_middleware


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

i18n_middleware.setup(dp)

dp.include_router(registration_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
