from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import gettext as _v
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
from app.utils import get_profile_card

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

    card = await get_profile_card(match, user)
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
        return await show_menu(message, state)

    match = await get_nth_last_reacted_match(user, rewind_index)
    if not match:
        await message.answer(_("No more matches to rewind"))
        await show_menu(message, state)
        return

    if with_keyboard:
        await message.answer(_("⏪ Rewinding"), reply_markup=get_search_keyboard())

    card = await get_profile_card(match, user)
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
    builder1, builder2 = InlineKeyboardBuilder(), InlineKeyboardBuilder()
    builder1.add(
        types.InlineKeyboardButton(
            text=_v("Yes", locale=user.ui_language), callback_data="show_matches"
        ),
        types.InlineKeyboardButton(
            text=_v("No", locale=user.ui_language), callback_data="delete_message"
        ),
    )
    builder2.add(
        types.InlineKeyboardButton(
            text=_v("Yes", locale=match.ui_language), callback_data="show_matches"
        ),
        types.InlineKeyboardButton(
            text=_v("No", locale=match.ui_language), callback_data="delete_message"
        ),
    )
    # duplicate messages so pybabel could extract them
    msg1 = _v(
        "Congratulations. You have matched with {match.name}."
        "\nYou can have a chat with them by clicking this <a href='https://t.me/{match.phone_number}'>link</a>"
        "\n\nDo you want to see your matches?",
        locale=user.ui_language.name,
    )
    msg2 = _v(
        "Congratulations. You have matched with {match.name}."
        "\nYou can have a chat with them by clicking this <a href='https://t.me/{match.phone_number}'>link</a>"
        "\n\nDo you want to see your matches?",
        locale=match.ui_language.name,
    )

    try:
        await bot.send_message(
            user.telegram_id,
            msg1.format(match=match),
            parse_mode="HTML",
            reply_markup=builder1.as_markup(),
        )
        await bot.send_message(
            match.telegram_id,
            msg2.format(match=user),
            parse_mode="HTML",
            reply_markup=builder2.as_markup(),
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        pass
    finally:
        await bot.session.close()


async def notify_match(match: User):
    bot = Bot(token=settings.BOT_TOKEN)
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text=_v("Yes", locale=match.ui_language.name), callback_data="show_likes"
        ),
        types.InlineKeyboardButton(
            text=_v("No", locale=match.ui_language.name), callback_data="delete_message"
        ),
    )
    msg = _v(
        "Someone liked your profile. Do you want to see who liked you?",
        locale=match.ui_language.name,
    )
    try:
        await bot.send_message(match.telegram_id, msg, reply_markup=builder.as_markup())
    except (TelegramBadRequest, TelegramForbiddenError):
        pass
    finally:
        await bot.session.close()


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
