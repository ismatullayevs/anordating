from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import gettext as _v
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy import exc

from app.core.config import settings
from app.core.db import session_factory
from app.enums import ReactionType
from app.filters import IsActiveHumanUser, IsHuman
from app.handlers.likes import show_likes
from app.handlers.matches import show_matches
from app.handlers.menu import show_menu
from app.keyboards import get_empty_search_keyboard, get_search_keyboard
from app.matching.algorithm import get_best_match
from app.models.user import User
from app.queries import (
    create_or_update_reaction,
    get_nth_last_reacted_match,
    get_user,
    is_mutual,
)
from app.states import AppStates
from app.utils import get_profile_card, haversine_distance

router = Router()
router.message.filter(IsHuman())


@router.message(AppStates.menu, F.text == __("🔎 Watch profiles"), IsActiveHumanUser())
async def search(
    message: types.Message, state: FSMContext, user: User, with_keyboard: bool = True
):
    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)

    match = await get_best_match(user)
    if not match:
        await message.answer(
            _("No matches found"), reply_markup=get_empty_search_keyboard()
        )
        return await state.set_state(AppStates.search)

    if with_keyboard:
        await message.answer("🔎", reply_markup=get_search_keyboard())

    card = await get_profile_card(
        match,
        dist=haversine_distance(
            user.latitude, user.longitude, match.latitude, match.longitude
        ),
    )
    await message.answer_media_group(card)
    await state.update_data(match_id=match.id)
    await state.set_state(AppStates.search)


@router.message(AppStates.search, F.text == __("⏪ Rewind"), IsActiveHumanUser())
async def rewind_empty(message: types.Message, state: FSMContext, user: User):
    await rewind(message, state, user, with_keyboard=True)


@router.message(AppStates.search, F.text == "⏪", IsActiveHumanUser())
@router.message(AppStates.likes, F.text == "⏪", IsActiveHumanUser())
@router.message(AppStates.matches, F.text == "⏪", IsActiveHumanUser())
async def rewind(
    message: types.Message, state: FSMContext, user: User, with_keyboard: bool = False
):
    rewind_index = await state.get_value("rewind_index") or 0

    if rewind_index >= settings.REWIND_LIMIT:
        await message.answer(
            _("You can't rewind more than {rewind_limit} times").format(
                rewind_limit=settings.REWIND_LIMIT
            )
        )

    match = await get_nth_last_reacted_match(user, rewind_index)
    if not match:
        await message.answer(_("No more matches to rewind"))
        await show_menu(message, state)
        return

    if with_keyboard:
        await message.answer(_("⏪ Rewinding"), reply_markup=get_search_keyboard())

    card = await get_profile_card(
        match,
        dist=haversine_distance(
            user.latitude, user.longitude, match.latitude, match.longitude
        ),
    )
    await message.answer_media_group(card)
    await state.update_data(match_id=match.id)
    await state.update_data(rewind_index=rewind_index + 1)


@router.message(AppStates.search, F.text.in_(["👎", "👍"]), IsActiveHumanUser())
@router.message(AppStates.likes, F.text.in_(["👎", "👍"]), IsActiveHumanUser())
@router.message(AppStates.matches, F.text == "👎", IsActiveHumanUser())
async def react(message: types.Message, state: FSMContext, user: User):
    assert message.text
    current_state = await state.get_state()
    reactions = {
        "👍": ReactionType.like,
        "👎": ReactionType.dislike,
    }

    match_id = await state.get_value("match_id")
    assert match_id

    try:
        match = await get_user(id=match_id, is_active=True)
    except exc.NoResultFound:
        await message.answer(_("User not found"))
        if current_state == AppStates.likes.state:
            return await show_likes(message, state, user, with_keyboard=False)
        if current_state == AppStates.matches.state:
            return await show_matches(message, state, user)
        return await search(message, state, user, with_keyboard=False)

    reaction = await create_or_update_reaction(user, match, reactions[message.text])

    if message.text == "👍" and not reaction.is_match_notified:
        mutual = await is_mutual(reaction)
        if mutual:
            await notify_mutual(user, match)
        else:
            await notify_match(match)
        async with session_factory() as session:
            reaction.is_match_notified = True
            session.add(reaction)
            await session.commit()

    if current_state == AppStates.likes.state:
        return await show_likes(message, state, user, with_keyboard=False)
    if current_state == AppStates.matches.state:
        return await show_matches(message, state, user)
    return await search(message, state, user, with_keyboard=False)


async def notify_mutual(user: User, match: User):
    bot = Bot(token=settings.BOT_TOKEN)

    # duplicate messages so pybabel could extract them
    msg1 = _v(
        "Congratulations. You have matched with {match.name}."
        "\nYou can have a chat with them by clicking this <a href='https://t.me/{match.phone_number}'>link</a>"
        '\n\nClick "❤️ Matches" in /menu to see your matches',
        locale=user.ui_language.name,
    )
    msg2 = _v(
        "Congratulations. You have matched with {match.name}."
        "\nYou can have a chat with them by clicking this <a href='https://t.me/{match.phone_number}'>link</a>"
        '\n\nClick "❤️ Matches" in /menu to see your matches',
        locale=match.ui_language.name,
    )

    try:
        await bot.send_message(
            user.telegram_id,
            msg1.format(match=match),
            parse_mode="HTML",
        )
        await bot.send_message(
            match.telegram_id,
            msg2.format(match=user),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass


async def notify_match(match: User):
    bot = Bot(token=settings.BOT_TOKEN)
    msg = _v(
        'Someone liked your profile. Click "👍 Likes" button on the /menu to see them',
        locale=match.ui_language.name,
    )
    try:
        await bot.send_message(match.telegram_id, msg)
    except TelegramBadRequest:
        pass
