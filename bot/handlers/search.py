import asyncio
import logging

import httpx
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import gettext as _v
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import exc

from app.enums import ReactionType
from bot.config import settings
from bot.filters import IsHuman
from bot.handlers.likes import show_likes
from bot.handlers.matches import show_matches
from bot.handlers.menu import show_menu
from bot.keyboards import get_empty_search_keyboard, get_search_keyboard
from bot.services.match import get_best_match, get_rewinds
from bot.services.media import get_media
from bot.services.user import get_current_user
from bot.states import AppStates
from bot.utils import get_profile_card, send_message

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(IsHuman())


async def search_with_keyboard(message: types.Message, state: FSMContext) -> None:
    """Send a keyboard to the user to search for profiles."""
    await message.answer("🔎", reply_markup=get_search_keyboard())
    return await search(message, state)


@router.message(AppStates.menu, F.text == __("🔎 Watch profiles"))
async def search(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Send a keyboard to the user to search for profiles."""
    if not message.from_user:
        return None

    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)

    try:
        user = await get_current_user(message.from_user.id)
        match = await get_best_match(message.from_user.id)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        await message.answer(_("An error occurred while fetching data."))
        return await state.set_state(AppStates.search)
    if not match:
        await message.answer(
            _("No one left to match with right now."),
            reply_markup=get_empty_search_keyboard(),
        )
        return await state.set_state(AppStates.search)
    media = await get_media(match.id)

    card = await get_profile_card(match, media, user)
    await message.answer_media_group(card)
    await state.update_data(match_id=match.id)
    await state.set_state(AppStates.search)
    return None


@router.message(AppStates.search, F.text == __("⏪ Rewind"))
async def rewind_with_keyboard(message: types.Message, state: FSMContext) -> None:
    """Rewind to the previous match with keyboard."""
    await message.answer(_("⏪ Rewinding"), reply_markup=get_search_keyboard())
    await rewind(message, state)


@router.message(AppStates.search, F.text == "⏪")
@router.message(AppStates.likes, F.text == "⏪")
@router.message(AppStates.matches, F.text == "⏪")
async def rewind(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Rewind to the previous match."""
    if not message.from_user:
        return

    user = await get_current_user(message.from_user.id)
    rewind_index = await state.get_value("rewind_index") or 0
    try:
        rewinds = await get_rewinds(
            telegram_id=message.from_user.id,
            limit=1,
            offset=rewind_index,
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            await message.answer(
                _("You can't rewind more than {rewind_limit} times").format(
                    rewind_limit=settings.REWIND_LIMIT,
                ),
            )
        raise

    if not rewinds:
        await message.answer(_("No more matches to rewind"))
        await show_menu(message, state)
        return

    rewind = rewinds[0]
    media = await get_media(rewind.id)
    card = await get_profile_card(rewind, media, user)
    await message.answer_media_group(card)
    await state.update_data(match_id=rewind.id)
    await state.update_data(rewind_index=rewind_index + 1)


@router.message(AppStates.search, F.text.in_(["👎", "👍"]))
@router.message(AppStates.likes, F.text.in_(["👎", "👍"]))
@router.message(AppStates.matches, F.text == "👎")
async def react(message: types.Message, state: FSMContext) -> None:
    """Handle reactions to matches."""
    if not message.text:
        return None

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
            return await show_likes(message, state, user)
        if current_state == AppStates.matches.state:
            return await show_matches(message, state, user)
        return await search_with_keyboard(message, state)

    is_created, reaction = await create_or_update_reaction(
        user,
        match,
        reactions[message.text],
    )

    if message.text == "👍" and not reaction.is_match_notified:
        mutual = await is_mutual(reaction)
        if mutual:
            asyncio.ensure_future(notify_mutual(user, match))
        else:
            asyncio.ensure_future(notify_match(match))
        async with session_factory() as session:
            reaction.is_match_notified = True
            session.add(reaction)
            await session.commit()
    if not is_created and message.text == "👎":
        try:
            await delete_chat_between_users(user.id, match.id)
        except exc.NoResultFound:
            pass

    if current_state == AppStates.likes.state:
        return await show_likes(message, state, user)
    if current_state == AppStates.matches.state:
        return await show_matches(message, state, user)
    return await search_with_keyboard(message, state)


async def notify_mutual(user: User, match: User):
    # duplicate messages so pybabel could extract them
    mk1 = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=_("Start a chat"),
                    web_app=types.WebAppInfo(
                        url=f"{settings.APP_URL}/users/{match.id}/chat",
                    ),
                ),
            ],
        ],
    )
    mk2 = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=_("Start a chat"),
                    web_app=types.WebAppInfo(
                        url=f"{settings.APP_URL}/users/{user.id}/chat",
                    ),
                ),
            ],
        ],
    )
    msg1 = _v(
        "Congratulations 🎉. You have matched with {match.name}."
        "\nStart a chat with them by clicking the button below 👇",
        locale=user.ui_language.name,
    )
    msg2 = _v(
        "Congratulations 🎉. You have matched with {match.name}."
        "\nStart a chat with them by clicking the button below 👇",
        locale=match.ui_language.name,
    )

    try:
        await send_message(
            user.telegram_id,
            msg1.format(match=match),
            parse_mode="HTML",
            reply_markup=mk1,
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        pass

    try:
        await send_message(
            match.telegram_id,
            msg2.format(match=user),
            parse_mode="HTML",
            reply_markup=mk2,
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        pass


async def notify_match(match: User):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text=_v("Yes", locale=match.ui_language.name),
            callback_data="show_likes",
        ),
        types.InlineKeyboardButton(
            text=_v("No", locale=match.ui_language.name),
            callback_data="delete_message",
        ),
    )
    msg = _v(
        "Someone liked your profile. Do you want to see who liked you?",
        locale=match.ui_language.name,
    )
    try:
        await send_message(match.telegram_id, msg, reply_markup=builder.as_markup())
    except (TelegramBadRequest, TelegramForbiddenError):
        pass


@router.callback_query(F.data == "delete_message")
async def delete_message(callback: types.CallbackQuery):
    if callback.message and isinstance(callback.message, types.Message):
        await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == "show_matches")
async def show_matches_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await get_user(telegram_id=callback.from_user.id, is_active=True)
    await show_matches(callback.message, state, user)


@router.callback_query(F.data == "show_likes")
async def show_likes_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await get_user(telegram_id=callback.from_user.id, is_active=True)
    await show_likes(callback.message, state, user)
