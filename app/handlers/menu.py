from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.keyboards import get_menu_keyboard
from app.models.user import Report
from app.states import MenuStates, SearchStates, LikesStates, ProfileStates
from app.utils import get_user
from app.core.db import session_factory
from sqlalchemy import exc

router = Router()


@router.message(Command("menu"))
async def show_menu(message: types.Message, state: FSMContext):
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale})

    await message.answer("Menu", reply_markup=get_menu_keyboard())
    await state.set_state(MenuStates.menu)


@router.message(LikesStates.likes, F.text == __("✍️ Report"))
@router.message(SearchStates.search, F.text == __("✍️ Report"))
async def report(message: types.Message, state: FSMContext):
    match_id = state.get_value('match_id')
    if not match_id:
        from app.handlers.search import search
        await message.answer(_("No matches to report"))
        return await search(message, state, with_keyboard=False)

    await message.answer(_("What's the reason for reporting this user?"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SearchStates.report_reason)


@router.message(SearchStates.report_reason, F.text)
async def report_reason(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    match_id = await state.get_value('match_id')
    if not match_id:
        from app.handlers.search import search
        await message.answer(_("No matches to report"))
        return await search(message, state, with_keyboard=False)

    try:
        user = await get_user(telegram_id=message.from_user.id)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    try:
        match = await get_user(id=match_id)
    except exc.NoResultFound:
        return await message.answer(_("User not found"))

    async with session_factory() as session:
        report = Report(from_user_id=user.id,
                        to_user_id=match.id, reason=message.text)
        session.add(report)
        await session.commit()

    await message.answer(_("User has been reported"))
    await show_menu(message, state)


@router.message(SearchStates.search, F.text == __("⬅️ Menu"))
@router.message(LikesStates.likes, F.text == __("⬅️ Menu"))
@router.message(ProfileStates.profile, F.text == __("⬅️ Menu"))
async def back_to_menu(message: types.Message, state: FSMContext):
    await show_menu(message, state)
