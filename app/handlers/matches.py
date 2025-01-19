from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.filters import IsActiveHumanUser, IsHuman
from app.handlers.menu import show_menu
from app.models.user import User
from app.states import MenuStates
from app.keyboards import get_matches_keyboard
from app.utils import get_profile_card
from app.queries import get_matches


router = Router()
router.message.filter(IsHuman())


@router.message(MenuStates.menu, F.text == __("❤️ Matches"), IsActiveHumanUser())
async def show_matches(message: types.Message, state: FSMContext, user: User, with_keyboard: bool | None = True):
    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)

    matches = await get_matches(user, limit=1)
    if not matches:
        await message.answer(_("No matches found"))
        return await show_menu(message, state)

    if with_keyboard:
        await message.answer(_("Matches"), reply_markup=get_matches_keyboard())

    match = matches[0]
    profile = await get_profile_card(match)
    await state.update_data(match_id=match.id)
    await message.answer_media_group(profile)
    await state.set_state(MenuStates.matches)
