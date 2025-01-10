from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.handlers.registration import get_profile
from app.keyboards import get_menu_keyboard, get_search_keyboard
from app.matching.algorithm import get_best_match
from app.orm import get_user, get_user_by_telegram_id
from app.states import (MenuStates, SearchStates, LikesStates, ProfileStates,
                        MatchesStates, DeactivateStates, LanguageStates)

router = Router()


@router.message(Command("menu"))
async def show_menu(message, state: FSMContext):
    data = await state.get_data()
    await state.set_data({"locale": data.get("locale")})

    await message.answer("Menu", reply_markup=get_menu_keyboard())
    await state.set_state(MenuStates.menu)


@router.message(MenuStates.menu, F.text == __("🔎 Search"))
async def search(message, state: FSMContext):
    assert message.from_user

    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        return await message.answer(_("You need to create a profile first"))
    
    match_id = await get_best_match(user.id)
    if not match_id:
        return await message.answer(_("No matches found"))
    
    profile = await get_profile(match_id)
    await message.answer("Search", reply_markup=get_search_keyboard())
    await message.answer_media_group(profile)
    await state.set_state(SearchStates.search)


@router.message(SearchStates.search, F.text == "⏪")
async def rewind(message, state: FSMContext):
    await message.answer("Rewinded")


@router.message(SearchStates.search, F.text == "👎")
async def dislike(message, state: FSMContext):
    await message.answer("Disliked")


@router.message(SearchStates.search, F.text == "👍")
async def like(message, state: FSMContext):
    await message.answer("Liked")


@router.message(SearchStates.search, F.text == "✍️ Report")
async def report(message, state: FSMContext):
    await message.answer("Reported")


@router.message(SearchStates.search, F.text == __("⬅️ Menu"))
@router.message(LikesStates.likes, F.text == __("⬅️ Menu"))
async def back_to_menu(message, state: FSMContext):
    await message.answer("Menu", reply_markup=get_menu_keyboard())
    await state.set_state(MenuStates.menu)


@router.message(MenuStates.menu, F.text == __("👍 Likes"))
async def show_likes(message, state: FSMContext):
    await message.answer("Likes", reply_markup=get_search_keyboard())
    await state.set_state(LikesStates.likes)


@router.message(Command('getstate'))
async def get_state(message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Current state: {current_state}")