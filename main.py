import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.handlers import router
from app.middlewares import i18n_middleware


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(i18n_middleware)
dp.callback_query.middleware(i18n_middleware)

dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
