import re
from aiogram import Bot, Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from aiogram.exceptions import TelegramBadRequest
from app.core.config import settings
from app.enums import ReactionType
from app.handlers.registration import get_profile_card
from app.keyboards import get_empty_search_keyboard, get_menu_keyboard, get_search_keyboard
from app.matching.algorithm import get_best_match
from app.models.user import Reaction, Report, User
from app.states import (MenuStates, SearchStates, LikesStates, ProfileStates,
                        MatchesStates, DeactivateStates, LanguageStates)
from app.utils import get_user, get_profile_card
from app.core.db import session_factory
from sqlalchemy import exc, select

router = Router()


@router.message(Command("menu"))
async def show_menu(message: types.Message, state: FSMContext):
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale})

    await message.answer("Menu", reply_markup=get_menu_keyboard())
    await state.set_state(MenuStates.menu)


@router.message(MenuStates.menu, F.text == __("🔎 Search"))
async def search(message: types.Message, state: FSMContext, with_keyboard: bool = True):
    assert message.from_user

    try:
        user = await get_user(telegram_id=message.from_user.id, with_preferences=True)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    match = await get_best_match(user)
    if not match:
        await message.answer(_("No matches found"),
                             reply_markup=get_empty_search_keyboard())
        return await state.set_state(SearchStates.search)

    if with_keyboard:
        await message.answer("🔎", reply_markup=get_search_keyboard())

    card = await get_profile_card(match)
    await message.answer_media_group(card)
    await state.update_data(match_id=match.id)
    await state.set_state(SearchStates.search)


@router.message(SearchStates.search, F.text == __("⏪ Rewind"))
async def rewind_empty(message: types.Message, state: FSMContext):
    await rewind(message, state, with_keyboard=True)


@router.message(SearchStates.search, F.text == "⏪")
async def rewind(message: types.Message, state: FSMContext, with_keyboard: bool = False):
    assert message.from_user
    rewind_index = await state.get_value("rewind_index") or 0

    try:
        user = await get_user(telegram_id=message.from_user.id)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    async with session_factory() as session:
        matches = (await session.scalars(select(Reaction.to_user_id)
                                         .where(Reaction.from_user_id == user.id)
                                         .order_by(Reaction.updated_at.desc())
                                         .limit(rewind_index + 1))).all()

    if len(matches) <= rewind_index:
        await message.answer(_("No more matches to rewind"))
        await show_menu(message, state)
        return
    
    if with_keyboard:
        await message.answer(_("⏪ Rewinding"), reply_markup=get_search_keyboard())

    match_id = matches[rewind_index]
    match = await get_user(id=match_id)
    card = await get_profile_card(match)
    await message.answer_media_group(card)
    await state.update_data(match_id=match.id)
    await state.update_data(rewind_index=rewind_index + 1)


@router.message(SearchStates.search, F.text.in_(["👎", "👍"]))
async def react(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    reactions = {
        "👍": ReactionType.like,
        "👎": ReactionType.dislike,
    }

    match_id = await state.get_value('match_id')
    if not match_id:
        await state.set_state(MenuStates.menu)
        return await message.answer(_("No matches to react"))
    
    match_id = int(match_id)
    try:
        user = await get_user(telegram_id=message.from_user.id)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    try:
        match = await get_user(id=match_id)
    except exc.NoResultFound:
        return await message.answer(_("User not found"))

    async with session_factory() as session:
        res = await session.scalars(select(Reaction)
                                    .where(Reaction.from_user_id == user.id,
                                           Reaction.to_user_id == match.id))
        try:
            reaction = res.one()
            if reaction.reaction_type == reactions[message.text]:
                return await message.answer(_("You've already {reaction_type}d this user")
                                            .format(reaction_type=reaction.reaction_type.name))
            reaction.reaction_type = reactions[message.text]
        except exc.NoResultFound:
            reaction = Reaction(from_user_id=user.id,
                                to_user_id=match.id,
                                reaction_type=reactions[message.text])

        session.add(reaction)
        await session.commit()

    if message.text == "👍":
        await notify_match(match)

    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)
    await search(message, state, with_keyboard=False)


async def notify_match(match: User):
    bot = Bot(token=settings.BOT_TOKEN)
    msg = _("You got a new match 🎉. Click \"👍 Likes\" button on the /menu")
    try:
        await bot.send_message(match.telegram_id, msg)
    except TelegramBadRequest:
        pass


@router.message(SearchStates.search, F.text == "✍️ Report")
async def report(message: types.Message, state: FSMContext):
    match_id = state.get_value('match_id')
    if not match_id:
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
async def back_to_menu(message: types.Message, state: FSMContext):
    await show_menu(message, state)
