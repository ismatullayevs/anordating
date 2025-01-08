from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from aiogram.utils.media_group import MediaGroupBuilder
from app.middlewares import i18n_middleware
from app.models.user import User
from app.core.db import session_factory
from app.filters import IsHumanUser
from app.keyboards import make_row_keyboard
from app.dto.file import FileAddDTO, FileRelThumbnailAddDTO
from app.dto.user import UserRelMediaAddDTO, UserRelMediaDTO, UserDTO
from app.enums import FileTypes, UILanguages, Genders
from app.utils import pydantic_to_sqlalchemy
from sqlalchemy import select
from sqlalchemy.orm import selectinload


router = Router()
router.message.filter(IsHumanUser())


class RegistrationStates(StatesGroup):
    language = State()
    name = State()
    age = State()
    gender = State()
    bio = State()
    media = State()
    location = State()


LANGUAGES = {
    "Uzbek 🇺🇿": UILanguages.uz,
    "Russian 🇷🇺": UILanguages.ru,
    "English 🇺🇸": UILanguages.en,
}

GENDERS = (
    (__("Male 👨‍🦱"), Genders.male),
    (__("Female 👩‍🦱"), Genders.female),
)


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    assert message.from_user
    await state.set_state(None)
    data = await state.get_data()
    await state.set_data({"locale": data.get("locale")})

    async with session_factory() as session:
        query = select(User).where(User.telegram_id ==
                                   message.from_user.id)
        result = await session.scalars(query)
        user = result.one_or_none()

    if user:
        await i18n_middleware.set_locale(state, user.ui_language.name)
        await get_me(message)
        return

    await message.answer(_("Hi! Please select a language"),
                         reply_markup=make_row_keyboard(LANGUAGES.keys()))
    await state.set_state(RegistrationStates.language)


@router.message(RegistrationStates.language, F.text.in_(LANGUAGES.keys()))
async def set_language(message: types.Message, state: FSMContext):
    assert message.text

    language = LANGUAGES[message.text]
    await i18n_middleware.set_locale(state, language.name)
    await state.update_data({"language": language})

    await message.answer(_("What is your name?"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.name)


@router.message(RegistrationStates.language)
async def set_language_invalid(message: types.Message):
    await message.answer(_("Please select a correct language"))


@router.message(RegistrationStates.name)
async def set_name(message: types.Message, state: FSMContext):
    assert message.text

    await state.update_data(name=message.text)

    await state.set_state(RegistrationStates.age)
    await message.answer(_("How old are you?"))


@router.message(RegistrationStates.age)
async def set_age(message: types.Message, state: FSMContext):
    assert message.text

    try:
        age = int(message.text)
    except ValueError:
        await message.answer(_("Please enter a valid number"))
        return

    await state.update_data(age=age)

    await message.answer(_("What is your gender?"),
                         reply_markup=make_row_keyboard(x[0].value for x in GENDERS))
    await state.set_state(RegistrationStates.gender)


@router.message(RegistrationStates.gender, F.text.in_([x[0] for x in GENDERS]))
async def set_gender(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    gender = None
    for k, v in GENDERS:
        if k == message.text:
            gender = v

    await state.update_data(gender=gender)

    await message.answer(_("Tell us about yourself"),
                         reply_markup=make_row_keyboard([_("Skip")]))
    await state.set_state(RegistrationStates.bio)


@router.message(RegistrationStates.gender)
async def set_gender_invalid(message: types.Message):
    await message.answer(_("Please select a correct gender"))


@router.message(RegistrationStates.bio, F.text == __("Skip"))
async def skip_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=None)

    await message.answer(_("Please upload photos of yourself"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.media)


@router.message(RegistrationStates.bio)
async def set_bio(message: types.Message, state: FSMContext):
    assert message.text

    await state.update_data(bio=message.text)

    await message.answer(_("Please upload photos of yourself"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.media)


@router.message(RegistrationStates.media, F.text == __("Continue"))
async def continue_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "media" not in data:
        await message.answer(_("Please upload at least one photo"))
        return

    await message.answer(_("Please share your location"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.location,)


@router.message(RegistrationStates.media, F.photo | F.video)
async def set_media(message: types.Message, state: FSMContext):
    file = None
    if message.photo:
        p = message.photo[-1]
        file = FileAddDTO(
            telegram_id=p.file_id,
            telegram_unique_id=p.file_unique_id,
            file_type=FileTypes.image,
            path=None,
            duration=None,
            file_size=p.file_size,
            mime_type=None,
        )
    elif message.video:
        if message.video.thumbnail:
            p = message.video.thumbnail
            thumbnail = FileAddDTO(
                telegram_id=p.file_id,
                telegram_unique_id=p.file_unique_id,
                file_type=FileTypes.image,
                path=None,
                duration=None,
                file_size=p.file_size,
                mime_type=None,
            )
            file = FileRelThumbnailAddDTO(
                telegram_id=message.video.file_id,
                telegram_unique_id=message.video.file_unique_id,
                file_type=FileTypes.video,
                path=None,
                duration=message.video.duration,
                file_size=message.video.file_size,
                mime_type=message.video.mime_type,
                thumbnail=thumbnail,
            )
    if file is None:
        await message.answer(_("Please upload a photo or video"))
        return

    data = await state.get_data()
    media = data["media"] if "media" in data else []
    media.append(file)
    data["media"] = media
    await state.set_data(data)

    await message.answer(_("Media has been uploaded. Upload more photos if you want or press \"Continue\""),
                         reply_markup=make_row_keyboard([_("Continue")]))


@router.message(RegistrationStates.location, F.location)
async def set_location(message: types.Message, state: FSMContext):
    assert message.location and message.from_user

    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)

    data = await state.get_data()
    user = UserRelMediaAddDTO(
        telegram_id=message.from_user.id,
        name=data["name"],
        age=data["age"],
        bio=data["bio"],
        gender=data["gender"],
        ui_language=data["language"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        media=data["media"],
    )

    user_db: User = pydantic_to_sqlalchemy(user)
    async with session_factory() as session:
        session.add(user_db)
        data = await session.commit()

    await state.set_state(None)
    data = await state.get_data()
    await state.set_data({"locale": data.get("locale")})
    await message.answer(_("Registration has been completed!"))
    await get_me(message)


@router.message(Command('me'))
async def get_me(message: types.Message):
    assert message.from_user

    async with session_factory() as session:
        query = select(User).where(User.telegram_id ==
                                   message.from_user.id).options(selectinload(User.media))
        result = await session.scalars(query)
        user = result.one_or_none()

    if not user:
        await message.answer(_("You are not registered!"))
        return

    user_dto = UserRelMediaDTO.model_validate(user, from_attributes=True)
    caption = ", ".join(
        v for v in [user_dto.name, str(user_dto.age), user_dto.bio] if v)
    album_builder = MediaGroupBuilder(
        caption=caption
    )
    for media in user_dto.media:
        if media.file_type == FileTypes.image:
            album_builder.add_photo(media.telegram_id or media.path or '')
        elif media.file_type == FileTypes.video:
            album_builder.add_video(media.telegram_id or media.path or '')

    await message.answer_media_group(album_builder.build())


@router.message(Command('delete'))
async def delete_me(message: types.Message):
    assert message.from_user

    async with session_factory() as session:
        query = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.scalars(query)
        user = result.one_or_none()

    if not user:
        await message.answer(_("You are not registered!"))
        return

    async with session_factory() as session:
        await session.delete(user)
        await session.commit()

    await message.answer("Your account has been deleted!")
