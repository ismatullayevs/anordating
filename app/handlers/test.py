from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.filters import IsHumanUser
from app.handlers.menu import show_menu
from app.models.user import User
from app.utils import get_profile_card

router = Router()


@router.message(Command("getdata"))
async def get_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(str(data))


@router.message(Command("getstate"))
async def get_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Current state: {current_state}")


@router.message(Command("me"), IsHumanUser())
async def get_me(message: types.Message, state: FSMContext, user: User):
    assert message.from_user
    profile = await get_profile_card(user)
    await message.answer_media_group(profile)
    await show_menu(message, state)
