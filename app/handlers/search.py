from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from aiogram.exceptions import TelegramBadRequest
from app.core.config import settings
from app.filters import IsActiveHumanUser, IsHuman
from app.handlers.menu import show_menu
from app.handlers.registration import get_profile_card
from app.keyboards import get_empty_search_keyboard, get_search_keyboard
from app.matching.algorithm import get_best_match
from app.models.user import Reaction, User
from app.states import MenuStates, SearchStates
from app.utils import get_profile_card
from app.queries import create_or_update_reaction, get_user
from app.core.db import session_factory
from app.enums import ReactionType
from sqlalchemy import exc, select

router = Router()
router.message.filter(IsHuman())


@router.message(MenuStates.menu, F.text == __("🔎 Search"), IsActiveHumanUser())
async def search(message: types.Message, state: FSMContext, user: User, with_keyboard: bool = True):
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


@router.message(SearchStates.search, F.text == __("⏪ Rewind"), IsActiveHumanUser())
async def rewind_empty(message: types.Message, state: FSMContext, user: User):
    await rewind(message, state, user, with_keyboard=True)


@router.message(SearchStates.search, F.text == "⏪", IsActiveHumanUser())
async def rewind(message: types.Message, state: FSMContext, user: User, with_keyboard: bool = False):
    rewind_index = await state.get_value("rewind_index") or 0

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


@router.message(SearchStates.search, F.text.in_(["👎", "👍"]), IsActiveHumanUser())
async def react(message: types.Message, state: FSMContext, user: User):
    assert message.text
    reactions = {
        "👍": ReactionType.like,
        "👎": ReactionType.dislike,
    }

    match_id = await state.get_value('match_id')
    assert match_id

    match_id = int(match_id)
    try:
        match = await get_user(id=match_id, is_active=True)
    except exc.NoResultFound:
        return await message.answer(_("User not found"))
    
    await create_or_update_reaction(user, match, reactions[message.text])

    if message.text == "👍":
        await notify_match(match)

    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)
    await search(message, state, with_keyboard=False)


async def notify_match(match: User, mutual: bool = False):
    bot = Bot(token=settings.BOT_TOKEN)
    msg = _("You got a new match 🎉. Click \"👍 Likes\" button on the /menu")
    if mutual:
        msg = _(
            "You got a new mutual match 🎉. Click \"❤️ Matches\" button on the /menu")
    try:
        await bot.send_message(match.telegram_id, msg)
    except TelegramBadRequest:
        pass
