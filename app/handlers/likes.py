from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.enums import ReactionType
from app.filters import IsActiveHumanUser, IsHuman
from app.handlers.menu import show_menu
from app.handlers.search import notify_match
from app.models.user import User
from app.states import MenuStates, LikesStates
from app.keyboards import get_search_keyboard
from app.utils import get_profile_card
from app.queries import create_or_update_reaction, get_likes, get_user
from sqlalchemy import exc


router = Router()
router.message.filter(IsHuman())


@router.message(MenuStates.menu, F.text == __("👍 Likes"), IsActiveHumanUser())
async def show_likes(message: types.Message, state: FSMContext, user: User):
    likes = await get_likes(user, limit=1)
    if not likes:
        await message.answer(_("No likes found"))
        return show_menu(message, state)

    await message.answer(_("Likes"), reply_markup=get_search_keyboard())

    match = likes[0]
    profile = await get_profile_card(match)
    await state.update_data(match_id=match.id)
    await message.answer_media_group(profile)
    await state.set_state(LikesStates.likes)


@router.message(LikesStates.likes, F.text.in_(["👍", "👎"]), IsActiveHumanUser())
async def react_to_liked(message: types.Message, state: FSMContext, user: User):
    assert message.text
    reactions = {
        "👍": ReactionType.like,
        "👎": ReactionType.dislike,
    }

    match_id = await state.get_value('match_id')
    assert match_id

    try:
        match = await get_user(id=match_id, is_active=True)
    except exc.NoResultFound:
        return await message.answer(_("User not found"))
    reaction = await create_or_update_reaction(user, match, reactions[message.text])

    if message.text == "👍":
        await notify_match(match, mutual=True)   # TODO: change this function

    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)
    await show_likes(message, state)
