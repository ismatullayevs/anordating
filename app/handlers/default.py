from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from app.handlers.registration import cmd_start

router = Router()


@router.message()
async def default_handler(message: types.Message, state: FSMContext):
    await cmd_start(message, state)
