from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(
                command="/menu",
                description="Menu",
            ),
            BotCommand(
                command="/help",
                description="Help",
            ),
        ],
        scope=BotCommandScopeAllPrivateChats(),
        language_code="en",
    )

    await bot.set_my_commands(
        [
            BotCommand(
                command="/menu",
                description="Menyu",
            ),
            BotCommand(
                command="/help",
                description="Yordam",
            ),
        ],
        scope=BotCommandScopeAllPrivateChats(),
        language_code="uz",
    )

    await bot.set_my_commands(
        [
            BotCommand(
                command="/menu",
                description="Меню",
            ),
            BotCommand(
                command="/help",
                description="Помощь",
            ),
        ],
        scope=BotCommandScopeAllPrivateChats(),
        language_code="ru",
    )
