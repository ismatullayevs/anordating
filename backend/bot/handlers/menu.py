from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy import update

from shared.core.db import session_factory
from bot.filters import IsActiveHumanUser, IsHuman, IsInactiveHumanUser
from bot.keyboards import (
    LANGUAGES,
    get_languages_keyboard,
    get_menu_keyboard,
    get_settings_keyboard,
    make_keyboard,
)
from bot.middlewares import i18n_middleware
from shared.models.user import Report, User
from shared.queries import get_user
from bot.states import AppStates

router = Router()
router.message.filter(IsHuman())


@router.message(F.text == __("⬅️ Menu"))
@router.message(Command("menu"))
async def show_menu(message: types.Message, state: FSMContext):
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale})

    await message.answer(_("Menu"), reply_markup=get_menu_keyboard())
    await state.set_state(AppStates.menu)


@router.message(AppStates.likes, F.text == __("✍️ Report"))
@router.message(AppStates.search, F.text == __("✍️ Report"))
@router.message(AppStates.matches, F.text == __("✍️ Report"))
async def report(message: types.Message, state: FSMContext):
    await message.answer(
        _("What's the reason for reporting this user?"),
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AppStates.report_reason)


@router.message(AppStates.report_reason, F.text, IsActiveHumanUser())
async def report_reason(message: types.Message, state: FSMContext, user: User):
    assert message.text

    match_id = await state.get_value("match_id")
    match = await get_user(id=match_id)

    async with session_factory() as session:
        report = Report(from_user_id=user.id, to_user_id=match.id, reason=message.text)
        session.add(report)
        await session.commit()

    await message.answer(_("User has been reported"))
    await show_menu(message, state)


@router.message(AppStates.menu, F.text == __("⚙️ Settings"))
async def show_settings(message: types.Message, state: FSMContext):
    await message.answer(_("Settings"), reply_markup=get_settings_keyboard())
    await state.set_state(AppStates.settings)


@router.message(AppStates.settings, F.text == __("⛔️ Deactivate"))
async def deactivate_account(message: types.Message, state: FSMContext):
    msg = _(
        "Are you sure you want to deactivate your account? "
        "No one will see your account, even the users that you liked"
    )
    await message.answer(msg, reply_markup=make_keyboard([[_("Yes"), _("No")]]))
    await state.set_state(AppStates.deactivate_confirm)


@router.message(AppStates.deactivate_confirm, F.text == __("No"))
async def deactivate_account_reject(message: types.Message, state: FSMContext):
    await show_settings(message, state)


@router.message(AppStates.deactivate_confirm, F.text == __("Yes"), IsActiveHumanUser())
async def deactivate_account_confirm(
    message: types.Message, state: FSMContext, user: User
):
    async with session_factory() as session:
        user.is_active = False
        session.add(user)
        await session.commit()
    await activate_account_start(message, state)


@router.message(
    AppStates.deactivated, F.text == __("Activate my account"), IsInactiveHumanUser()
)
async def activate_account(message: types.Message, state: FSMContext, user: User):
    async with session_factory() as session:
        user.is_active = True
        session.add(user)
        await session.commit()

    await message.answer(_("Your account has been activated"))
    await show_menu(message, state)


async def activate_account_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Your account has been deactivated. To activate it, press the button below"),
        reply_markup=make_keyboard([[_("Activate my account")]]),
    )
    await state.set_state(AppStates.deactivated)


@router.message(AppStates.settings, F.text == __("🌐 Language"))
async def change_language_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Choose your language"), reply_markup=get_languages_keyboard()
    )
    await state.set_state(AppStates.update_ui_language)


@router.message(AppStates.update_ui_language, F.text.in_(LANGUAGES.keys()))
async def change_language(
    message: types.Message, state: FSMContext, from_user: types.User
):
    assert message.text
    await i18n_middleware.set_locale(state, LANGUAGES[message.text].name)
    await state.update_data(locale=LANGUAGES[message.text].name)

    async with session_factory() as session:
        query = (
            update(User)
            .where(User.telegram_id == from_user.id)
            .values(ui_language=LANGUAGES[message.text])
        )
        await session.execute(query)
        await session.commit()
    await show_settings(message, state)


@router.message(AppStates.settings, F.text == __("❌ Delete account"))
async def delete_account_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Are you sure you want to delete your account? All your data will be lost"),
        reply_markup=make_keyboard([[_("Yes"), _("No")]]),
    )
    await state.set_state(AppStates.delete_confirm)


@router.message(AppStates.delete_confirm, F.text == __("No"))
async def delete_account_reject(message: types.Message, state: FSMContext):
    await show_settings(message, state)


@router.message(AppStates.delete_confirm, F.text == __("Yes"), IsActiveHumanUser())
async def delete_account_confirm(message: types.Message, state: FSMContext, user: User):
    async with session_factory() as session:
        await session.delete(user)
        await session.commit()
    await start_registration_start(message, state)


async def start_registration_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Your account has been deleted. To start again, press the button below"),
        reply_markup=make_keyboard([[_("Start registration")]]),
    )
    await state.set_state(AppStates.deleted)
