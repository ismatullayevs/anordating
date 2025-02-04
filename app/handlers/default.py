from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

router = Router()


@router.message()
async def default_handler(message: types.Message, state: FSMContext):
    await message.answer(_("Unknown command. Please use /start to start the bot."))
