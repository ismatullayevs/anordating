from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from bot.filters import IsActiveHumanUser, IsHuman
from bot.handlers.menu import show_menu
from bot.keyboards import get_matches_keyboard
from shared.models.user import User
from shared.queries import get_matches
from bot.states import AppStates
from bot.utils import get_profile_card
from shared.core.config import settings

router = Router()
router.message.filter(IsHuman())


@router.message(AppStates.matches, F.text.in_(["⬅️", "➡️"]), IsActiveHumanUser())
@router.message(AppStates.menu, F.text == __("❤️ Matches"), IsActiveHumanUser())
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
    profile = await get_profile_card(match, user)
    await state.update_data(match_id=match.id)
    await message.answer_media_group(profile)

    # await message.answer(
    #     _(
    #         "You both liked each other. You can talk to them by clicking this "
    #         "<a href='https://t.me/{phone_number}'>link</a>"
    #     ).format(phone_number=match.phone_number),
    #     reply_markup=get_matches_keyboard(has_previous, has_next),
    #     parse_mode="HTML",
    # )
    await message.answer(
        _(
            "You both liked each other. Start a chat with them by clicking the button below."
        ),
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=_("Start a chat"),
                        web_app=types.WebAppInfo(
                            url=f"{settings.MINI_APP_URL}/users/{match.id}/chat",
                        ),
                    )
                ]
            ],
        ))

    await message.answer(
        _("Matches"),
        reply_markup=get_matches_keyboard(has_previous, has_next),
    )

    await state.set_state(AppStates.matches)
    await state.update_data(index=index)
