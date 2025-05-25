from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from bot.keyboards import LANGUAGES, make_keyboard
from bot.states import AppStates
from bot.utils import get_profile_card
from shared.queries import get_user

router = Router()


@router.message(Command("newuser"))
async def cmd_new_user(message: types.Message, state: FSMContext):
    assert message.from_user
    user = await get_user(telegram_id=message.from_user.id)
    if not user.is_superuser:
        await message.answer(_("Only superusers can use this command"))
        return

    await state.set_state(None)
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale, "testing": True})

    await message.answer(
        _("Hi! Select a language"),
        reply_markup=make_keyboard([list(LANGUAGES.keys())]),
    )
    await state.set_state(AppStates.set_ui_language)


@router.message(Command("getuser"))
async def cmd_get_user(message: types.Message, state: FSMContext):
    assert message.from_user and message.text
    user = await get_user(telegram_id=message.from_user.id)
    if not user.is_superuser:
        await message.answer(_("Only superusers can use this command"))
        return

    user_id = message.text.split(" ")[1]
    user = await get_user(id=user_id, with_media=True)
    card = await get_profile_card(user)
    await message.answer_media_group(card)


@router.message()
async def default_handler(message: types.Message, state: FSMContext):
    await message.answer(_("Unknown command. Please use /start to start the bot."))
