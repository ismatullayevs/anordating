from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from bot.filters import IsActiveHumanUser, IsHuman
from bot.handlers.menu import show_menu
from bot.keyboards import get_search_keyboard
from shared.models.user import User
from shared.queries import get_likes
from bot.states import AppStates
from bot.utils import get_profile_card

router = Router()
router.message.filter(IsHuman())


@router.message(AppStates.menu, F.text == __("👍 Likes"), IsActiveHumanUser())
async def show_likes(
    message: types.Message,
    state: FSMContext,
    user: User,
    with_keyboard: bool | None = True,
):
    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)

    likes = await get_likes(user, limit=1)
    if not likes:
        await message.answer(_("No likes found"))
        return await show_menu(message, state)

    if with_keyboard:
        await message.answer(_("Likes"), reply_markup=get_search_keyboard())

    match = likes[0]
    profile = await get_profile_card(match, user)
    await state.update_data(match_id=match.id)
    await message.answer_media_group(profile)
    await state.set_state(AppStates.likes)
