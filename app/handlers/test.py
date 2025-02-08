from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.filters import IsHumanUser
from app.handlers.menu import show_menu
from app.keyboards import make_keyboard
from app.handlers.registration import LANGUAGES
from app.models.user import User
from app.states import AppStates
from app.queries import get_user
from app.core.db import session_factory
from sqlalchemy.exc import NoResultFound

from app.utils import get_profile_card

router = Router()


@router.message(Command("getdata"))
async def get_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(str(data))


@router.message(Command("getstate"))
async def get_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Current state: {current_state}")


@router.message(Command("newuser"))
async def cmd_new_user(message: types.Message, state: FSMContext):
    assert message.from_user
    await state.set_state(None)
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale, "testing": True})

    await message.answer(
        _("Hi! Please select a language"),
        reply_markup=make_keyboard([list(LANGUAGES.keys())]),
    )
    await state.set_state(AppStates.set_ui_language)


@router.message(Command("me"), IsHumanUser())
async def get_me(message: types.Message, state: FSMContext, user: User):
    assert message.from_user
    profile = await get_profile_card(user)
    await message.answer_media_group(profile)
    await show_menu(message, state)


@router.message(Command("delete"))
async def delete_me(message: types.Message):
    assert message.from_user

    try:
        user = await get_user(telegram_id=message.from_user.id)
    except NoResultFound:
        await message.answer(_("You are not registered!"))
        return

    async with session_factory() as session:
        await session.delete(user)
        await session.commit()

    await message.answer("Your account has been deleted!")
