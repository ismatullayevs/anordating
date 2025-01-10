from random import randint
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from aiogram.utils.media_group import MediaGroupBuilder
from app.middlewares import i18n_middleware
from app.models.user import User
from app.core.db import session_factory
from app.filters import IsHumanUser
from app.keyboards import get_menu_keyboard, make_row_keyboard
from app.dto.file import FileAddDTO
from app.dto.user import PreferenceAddDTO, UserRelAddDTO, UserRelMediaDTO
from app.enums import FileTypes, PreferredGenders, UILanguages, Genders
from app.orm import get_user_by_telegram_id
from app.states import MenuStates, RegistrationStates
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json


router = Router()
router.message.filter(IsHumanUser())


LANGUAGES = {
    "Uzbek 🇺🇿": UILanguages.uz,
    "Russian 🇷🇺": UILanguages.ru,
    "English 🇺🇸": UILanguages.en,
}


# use `__` so that pybabel could extract strings for translation
GENDERS = (
    (__("Male 👨‍🦱"), Genders.male),
    (__("Female 👩‍🦱"), Genders.female),
)

GENDER_PREFERENCES = (
    (__("Men 👨‍🦱"), PreferredGenders.male),
    (__("Women 👩‍🦱"), PreferredGenders.female),
    (__("Friends 👫"), PreferredGenders.friends),
)


@router.message(Command("newuser"))
async def cmd_new_user(message: types.Message, state: FSMContext):
    assert message.from_user
    await state.set_state(None)
    data = await state.get_data()
    await state.set_data({"locale": data.get("locale"), "testing": True})

    await message.answer(_("Hi! Please select a language"),
                         reply_markup=make_row_keyboard(LANGUAGES.keys()))
    await state.set_state(RegistrationStates.language)


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


@router.message(RegistrationStates.name, F.text)
async def set_name(message: types.Message, state: FSMContext):
    assert message.text

    if not 3 <= len(message.text) <= 30:
        await message.answer(_("Name must be between 3 and 30 characters"))
        return

    await state.update_data(name=message.text)
    await message.answer(_("How old are you?"))
    await state.set_state(RegistrationStates.age)


@router.message(RegistrationStates.age, F.text)
async def set_age(message: types.Message, state: FSMContext):
    assert message.text

    if not message.text.isdigit():
        await message.answer(_("Please enter a valid age"))
        return

    age = int(message.text)
    if not 18 <= age <= 100:
        await message.answer(_("You must be between 18 and 100 years old"))
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


@router.message(RegistrationStates.bio, F.text == __("Skip"))
async def skip_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=None)
    await message.answer(_("Please upload photos of yourself"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.media)


@router.message(RegistrationStates.bio, F.text)
async def set_bio(message: types.Message, state: FSMContext):
    assert message.text
    if len(message.text) > 255:
        await message.answer(_("Bio must be less than 255 characters"))
        return

    await state.update_data(bio=message.text)
    await message.answer(_("Please upload photos of yourself"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.media)


@router.message(RegistrationStates.media, F.text == __("Continue"))
async def continue_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "media" not in data or not data["media"]:
        await message.answer(_("Please upload at least one photo"))
        return

    await message.answer(_("Please share your location"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.location)


@router.message(RegistrationStates.media, F.photo | F.video)
async def set_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "media" in data and isinstance(data["media"], list) and len(data["media"]) >= 3:
        await message.answer(_("You can upload at most 3 media"))
        await message.answer(_("Please share your location"),
                             reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.location)
        return

    file = None
    if message.photo:
        p = message.photo[-1]
        file = {
            "telegram_id": p.file_id,
            "telegram_unique_id": p.file_unique_id,
            "file_type": FileTypes.image,
            "path": None,
            "duration": None,
            "file_size": p.file_size,
            "mime_type": None,
        }

    elif message.video:
        if message.video.thumbnail:
            p = message.video.thumbnail
            thumbnail = {
                "telegram_id": p.file_id,
                "telegram_unique_id": p.file_unique_id,
                "file_type": FileTypes.image,
                "path": None,
                "duration": None,
                "file_size": p.file_size,
                "mime_type": None,
            }
            file = {
                "telegram_id": message.video.file_id,
                "telegram_unique_id": message.video.file_unique_id,
                "file_type": FileTypes.video,
                "path": None,
                "duration": message.video.duration,
                "file_size": message.video.file_size,
                "mime_type": message.video.mime_type,
                "thumbnail": thumbnail,
            }
    assert file is not None

    media = data["media"] if "media" in data and isinstance(
        data["media"], list) else []
    media.append(json.dumps(file))
    data["media"] = media
    await state.set_data(data)

    if len(media) < 3:
        await message.answer(_("Media has been uploaded. Upload more photos if you want or press \"Continue\""),
                             reply_markup=make_row_keyboard([_("Continue")]))
    else:
        await message.answer(_("Please share your location"),
                             reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.location)


@router.message(RegistrationStates.location, F.location)
async def set_location(message: types.Message, state: FSMContext):
    assert message.location and message.from_user

    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)

    await message.answer(_("What kind of people do you want to see?"),
                         reply_markup=make_row_keyboard(x[0].value for x in GENDER_PREFERENCES))
    await state.set_state(RegistrationStates.gender_preferences)


@router.message(RegistrationStates.gender_preferences, F.text.in_([x[0] for x in GENDER_PREFERENCES]))
async def set_preferred_gender(message: types.Message, state: FSMContext):
    preferred_gender = None
    for k, v in GENDER_PREFERENCES:
        if k == message.text:
            preferred_gender = v
    assert preferred_gender

    await state.update_data(preferred_gender=preferred_gender)
    await message.answer(_("What is your preferred age range? (e.g. 18-25)"),
                         reply_markup=make_row_keyboard([_("Skip")]))
    await state.set_state(RegistrationStates.age_preferences)


@router.message(RegistrationStates.age_preferences, F.text == __("Skip"))
async def skip_age_preferences(message: types.Message, state: FSMContext):
    await state.update_data(preferred_min_age=None)
    await state.update_data(preferred_max_age=None)
    await save_user(message, state)


@router.message(RegistrationStates.age_preferences, F.text)
async def set_age_preferences(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    try:
        min_age, max_age = map(int, message.text.split("-"))
    except ValueError:
        return await message.answer(_("Please enter a valid age range"))

    if not min_age < max_age:
        return await message.answer(_("Min age must be less than max age"))
    if not 18 <= min_age < max_age <= 100:
        return await message.answer(_("Age range must be between 18 and 100"))

    await state.update_data(preferred_min_age=min_age)
    await state.update_data(preferred_max_age=max_age)

    await save_user(message, state)


async def save_user(message: types.Message, state: FSMContext):
    assert message.from_user
    data = await state.get_data()
    media = []
    for m in data["media"]:
        v = json.loads(m)
        media.append(FileAddDTO.model_validate(v))

    preferences = PreferenceAddDTO(
        min_age=data["preferred_min_age"],
        max_age=data["preferred_max_age"],
        preferred_gender=data["preferred_gender"]
    )

    if "testing" in data and data["testing"]:
        telegram_id = randint(1000000000, 9999999999) # TODO: remove after testing
    else:
        telegram_id = message.from_user.id

    user = UserRelAddDTO(
        telegram_id=telegram_id,
        name=data["name"],
        age=data["age"],
        bio=data["bio"],
        gender=data["gender"],
        ui_language=data["language"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        media=media,
        preferences=preferences
    )

    user_db = user.to_orm()
    async with session_factory() as session:
        session.add(user_db)
        data = await session.commit()

    await state.set_state(MenuStates.menu)
    data = await state.get_data()
    await state.set_data({"locale": data.get("locale")})
    await message.answer(_("Registration has been completed!"),
                         reply_markup=get_menu_keyboard())
    await get_me(message)


@router.message(Command('me'))
async def get_me(message: types.Message):
    assert message.from_user
    user = await get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer(_("You are not registered!"))
        return
    
    profile = await get_profile(user.id)
    await message.answer_media_group(profile)


async def get_profile(id: int):
    async with session_factory() as session:
        query = select(User).where(User.id ==
                                   id).options(selectinload(User.media))
        result = await session.scalars(query)
        user = result.one_or_none()


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

    return album_builder.build()


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
