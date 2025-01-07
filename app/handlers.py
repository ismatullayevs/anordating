from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.middlewares import i18n_middleware
from app.models.user import User
from app.core.db import session_factory
from app.filters import IsHumanUser
from sqlalchemy import select

router = Router()
router.message.filter(IsHumanUser())


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if not message.from_user or message.from_user.is_bot:
        return

    async with session_factory() as session:
        query = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.scalars(query)
        user = result.one_or_none()

    if user:
        await i18n_middleware.set_locale(state, "uz")
        await message.answer(_("Hello, {name}!").format(name=user.name))
        return
