from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.enums import ReactionType
from app.handlers.menu import notify_match, show_menu
from app.models.user import Reaction
from app.states import MenuStates, LikesStates
from app.keyboards import get_search_keyboard
from app.utils import get_likes, get_profile_card, get_user
from app.core.db import session_factory
from sqlalchemy import exc, select


router = Router()


@router.message(MenuStates.menu, F.text == __("👍 Likes"))
async def show_likes(message: types.Message, state: FSMContext):
    assert message.from_user

    try:
        user = await get_user(telegram_id=message.from_user.id)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

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


@router.message(LikesStates.likes, F.text.in_(["👍", "👎"]))
async def react_to_liked(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    reactions = {
        "👍": ReactionType.like,
        "👎": ReactionType.dislike,
    }

    match_id = await state.get_value('match_id')
    if not match_id:
        await state.set_state(MenuStates.menu)
        return await message.answer(_("No matches to react"))

    match_id = int(match_id)
    try:
        user = await get_user(telegram_id=message.from_user.id)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    try:
        match = await get_user(id=match_id)
    except exc.NoResultFound:
        return await message.answer(_("User not found"))

    async with session_factory() as session:
        res = await session.scalars(select(Reaction)
                                    .where(Reaction.from_user_id == user.id,
                                           Reaction.to_user_id == match.id))
        try:
            reaction = res.one()
            if reaction.reaction_type == reactions[message.text]:
                return await message.answer(_("You've already {reaction_type}d this user")
                                            .format(reaction_type=reaction.reaction_type.name))
            reaction.reaction_type = reactions[message.text]
        except exc.NoResultFound:
            reaction = Reaction(from_user_id=user.id,
                                to_user_id=match.id,
                                reaction_type=reactions[message.text])

        session.add(reaction)
        await session.commit()

    if message.text == "👍":
        await notify_match(match, mutual=True)   # TODO: change this function

    await state.update_data(match_id=None)
    await state.update_data(rewind_index=0)
    await show_likes(message, state)
