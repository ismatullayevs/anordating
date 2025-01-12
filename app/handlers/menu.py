from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.enums import ReactionType
from app.handlers.registration import get_profile_card
from app.keyboards import get_menu_keyboard, get_search_keyboard
from app.matching.algorithm import get_best_match
from app.models.user import Reaction
from app.states import (MenuStates, SearchStates, LikesStates, ProfileStates,
                        MatchesStates, DeactivateStates, LanguageStates)
from app.utils import get_user, get_profile_card
from app.core.db import session_factory
from sqlalchemy import exc, select

router = Router()


@router.message(Command("menu"))
async def show_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_data({"locale": data.get("locale")})

    await message.answer("Menu", reply_markup=get_menu_keyboard())
    await state.set_state(MenuStates.menu)


@router.message(MenuStates.menu, F.text == __("🔎 Search"))
async def search(message: types.Message, state: FSMContext):
    await message.answer("🔎", reply_markup=get_search_keyboard())
    await show_matches(message, state)
    await state.set_state(SearchStates.search)


async def show_matches(message: types.Message, state: FSMContext):
    assert message.from_user

    try:
        user = await get_user(telegram_id=message.from_user.id, with_preferences=True)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    match = await get_best_match(user)
    if not match:
        await state.set_state(MenuStates.menu)
        return await message.answer(_("No matches found"),
                                    reply_markup=get_menu_keyboard())

    profile = await get_profile_card(match)
    await message.answer_media_group(profile)
    await state.update_data(match_id=match.id)
    await state.set_state(SearchStates.search)


@router.message(SearchStates.search, F.text == "⏪")
async def rewind(message: types.Message, state: FSMContext):
    await message.answer("Rewinded")


@router.message(SearchStates.search, F.text.in_(["👎", "👍"]))
async def react(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    reactions = {
        "👍": ReactionType.like,
        "👎": ReactionType.dislike,
    }

    data = await state.get_data()
    match_id = data['match_id']
    if not match_id:
        await state.set_state(MenuStates.menu)
        return await message.answer(_("No matches to react"),
                                    reply_markup=get_menu_keyboard())

    match_id = int(match_id)
    try:
        user = await get_user(telegram_id=message.from_user.id)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    try:
        match = await get_user(id=match_id)
    except exc.NoResultFound:
        return await message.answer(_("User not found"))

    async with session_factory() as session:   # TODO: If reaction exists, update it
        res = await session.scalars(select(Reaction)
                              .where(Reaction.from_user_id == user.id,
                                     Reaction.to_user_id == match.id))
        try:
            reaction = res.one()
            reaction.reaction_type = reactions[message.text]
        except exc.NoResultFound:
            reaction = Reaction(from_user_id=user.id,
                                to_user_id=match.id,
                                reaction_type=reactions[message.text])

        session.add(reaction)
        await session.commit()

    await state.update_data(match_id=None)
    await show_matches(message, state)


@router.message(SearchStates.search, F.text == "✍️ Report")
async def report(message: types.Message, state: FSMContext):
    await message.answer("Reported")


@router.message(SearchStates.search, F.text == __("⬅️ Menu"))
@router.message(LikesStates.likes, F.text == __("⬅️ Menu"))
async def back_to_menu(message: types.Message, state: FSMContext):
    await message.answer("Menu", reply_markup=get_menu_keyboard())
    await state.set_state(MenuStates.menu)


@router.message(MenuStates.menu, F.text == __("👍 Likes"))
async def show_likes(message: types.Message, state: FSMContext):
    await message.answer("Likes", reply_markup=get_search_keyboard())
    await state.set_state(LikesStates.likes)


@router.message(Command('getstate'))
async def get_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Current state: {current_state}")
