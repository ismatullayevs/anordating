from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.filters import IsActiveHumanUser, IsHuman
from app.handlers.menu import show_menu
from app.models.user import User
from app.states import MenuStates
from app.keyboards import get_matches_keyboard
from app.utils import get_profile_card, haversine_distance
from app.queries import get_matches


router = Router()
router.message.filter(IsHuman())


@router.message(MenuStates.matches, F.text.in_(["⬅️", "➡️"]), IsActiveHumanUser())
@router.message(MenuStates.menu, F.text == __("❤️ Matches"), IsActiveHumanUser())
async def show_matches(message: types.Message, state: FSMContext, user: User):
    if message.text == _("❤️ Matches"):
        index = 0
    else:
        index = await state.get_value("index") or 0

    if message.text == "⬅️":
        index += 1
    elif message.text == "➡️" and index > 0:
        index -= 1

    has_previous, has_next = False, index > 0
    matches = await get_matches(user, limit=2, offset=index)
    if not matches:  # TODO: Return the last match instead
        await message.answer(_("No matches found"))
        return await show_menu(message, state)
    if len(matches) == 2:
        has_previous = True

    match = matches[0]
    profile = await get_profile_card(match, dist=haversine_distance(
        user.latitude, user.longitude, match.latitude, match.longitude))
    await state.update_data(match_id=match.id)
    await message.answer_media_group(profile)

    await message.answer(_("You both liked each other. You can talk to them by clicking this "
                           "<a href='https://t.me/{phone_number}'>link</a>")
                         .format(phone_number=match.phone_number),
                         reply_markup=get_matches_keyboard(has_previous, has_next),
                         parse_mode="HTML")
    await state.set_state(MenuStates.matches)
    await state.update_data(index=index)
