from random import randint
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.middlewares import i18n_middleware
from app.core.db import session_factory
from app.filters import IsHumanUser
from app.keyboards import (get_ask_location_keyboard, get_genders_keyboard, get_languages_keyboard,
                           get_menu_keyboard, get_preferred_genders_keyboard, make_keyboard, 
                           LANGUAGES, GENDERS, GENDER_PREFERENCES)
from app.dto.file import FileAddDTO
from app.dto.user import PreferenceAddDTO, UserRelAddDTO
from app.enums import FileTypes
from app.states import MenuStates, RegistrationStates
from app.utils import get_user
from app.utils import get_profile_card
from sqlalchemy.exc import NoResultFound


router = Router()
router.message.filter(IsHumanUser())


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    assert message.from_user
    await state.set_state(None)
    locale = await state.get_value('locale')
    await state.set_data({"locale": locale})

    try:
        user = await get_user(telegram_id=message.from_user.id, with_media=True)
        await i18n_middleware.set_locale(state, user.ui_language.name)

        from app.handlers.menu import show_menu
        await show_menu(message, state)
        await state.set_state(MenuStates.menu)
    except NoResultFound:
        await set_language_start(message, state)


async def set_language_start(message: types.Message, state: FSMContext):
    await message.answer(_("Hi! Please select a language"),
                         reply_markup=get_languages_keyboard())
    await state.set_state(RegistrationStates.language)


@router.message(RegistrationStates.language, F.text.in_(LANGUAGES.keys()))
async def set_language(message: types.Message, state: FSMContext):
    assert message.text
    language = LANGUAGES[message.text]

    await i18n_middleware.set_locale(state, language.name)
    await state.update_data({"language": language})

    await set_name_start(message, state)


@router.message(RegistrationStates.language)
async def set_language_invalid(message: types.Message, state: FSMContext):
    await message.answer(_("Please select one of the given languages"))


async def set_name_start(message: types.Message, state: FSMContext):
    await message.answer(_("What is your name?"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.name)


@router.message(RegistrationStates.name, F.text)
async def set_name(message: types.Message, state: FSMContext):
    assert message.text

    if len(message.text) < 3:
        return await message.answer(_("Name must be at least 3 characters long"))
    elif len(message.text) > 30:
        return await message.answer(_("Name must be less than 30 characters"))

    if not all(x.isalpha() or x.isspace() for x in message.text):
        return await message.answer(_("Name can only contain letters"))

    await state.update_data(name=message.text)
    await set_age_start(message, state)


async def set_age_start(message: types.Message, state: FSMContext):
    await message.answer(_("How old are you?"))
    await state.set_state(RegistrationStates.age)


@router.message(RegistrationStates.age, F.text)
async def set_age(message: types.Message, state: FSMContext):
    assert message.text

    try:
        age = int(message.text)
    except ValueError:
        return await message.answer(_("Please enter a number"))

    if age < 18:
        return await message.answer(_("You must be at least 18 years old to use this bot"))
    elif age > 100:
        return await message.answer(_("You must be less than 100 years old to use this bot"))

    await state.update_data(age=age)
    await set_gender_start(message, state)


async def set_gender_start(message: types.Message, state: FSMContext):
    await message.answer(_("What is your gender?"),
                         reply_markup=get_genders_keyboard())
    await state.set_state(RegistrationStates.gender)


@router.message(RegistrationStates.gender, F.text.in_([x[0] for x in GENDERS]))
async def set_gender(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    gender = None
    for k, v in GENDERS:
        if k == message.text:
            gender = v
            break

    await state.update_data(gender=gender)
    await set_bio_start(message, state)


@router.message(RegistrationStates.gender)
async def set_gender_invalid(message: types.Message):
    await message.answer(_("Please select one of the given options"))


async def set_bio_start(message: types.Message, state: FSMContext):
    msg = _("Tell us more about yourself. Who are you looking for?")
    await message.answer(msg, reply_markup=make_keyboard([[_("Skip")]]))
    await state.set_state(RegistrationStates.bio)


@router.message(RegistrationStates.bio, F.text == __("Skip"))
async def skip_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=None)
    await set_preferred_gender_start(message, state)


@router.message(RegistrationStates.bio, F.text)
async def set_bio(message: types.Message, state: FSMContext):
    assert message.text
    if len(message.text) > 255:
        await message.answer(_("Bio must be less than 255 characters"))
        return

    await state.update_data(bio=message.text)
    await set_preferred_gender_start(message, state)


async def set_preferred_gender_start(message: types.Message, state: FSMContext):
    await message.answer(_("Select preferred gender"),
                         reply_markup=get_preferred_genders_keyboard())
    await state.set_state(RegistrationStates.gender_preferences)


@router.message(RegistrationStates.gender_preferences, F.text.in_([x[0] for x in GENDER_PREFERENCES]))
async def set_preferred_gender(message: types.Message, state: FSMContext):
    preferred_gender = None
    for k, v in GENDER_PREFERENCES:
        if k == message.text:
            preferred_gender = v
            break
    assert preferred_gender

    await state.update_data(preferred_gender=preferred_gender)
    await set_age_preferences_start(message, state)


async def set_age_preferences_start(message: types.Message, state: FSMContext):
    await message.answer(_("What is your preferred age range? (e.g. 18-25)"),
                         reply_markup=make_keyboard([[_("Skip")]]))
    await state.set_state(RegistrationStates.age_preferences)


@router.message(RegistrationStates.age_preferences, F.text == __("Skip"))
async def skip_age_preferences(message: types.Message, state: FSMContext):
    await state.update_data(preferred_min_age=None)
    await state.update_data(preferred_max_age=None)
    await set_location_start(message, state)


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
    await set_location_start(message, state)


async def set_location_start(message: types.Message, state: FSMContext):
    await message.answer(_("Please share your location"),
                         reply_markup=get_ask_location_keyboard())
    await state.set_state(RegistrationStates.location)


@router.message(RegistrationStates.location, F.location)
async def set_location(message: types.Message, state: FSMContext):
    assert message.location and message.from_user

    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)
    await set_media_start(message, state)


async def set_media_start(message: types.Message, state: FSMContext):
    await message.answer(_("Please upload photos or videos of yourself"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.media)


@router.message(RegistrationStates.media, F.text == __("Continue"))
async def continue_registration(message: types.Message, state: FSMContext):
    media = await state.get_value("media")
    if not media:
        await message.answer(_("Please upload at least one photo"))
        return
    await finish_registration(message, state)


@router.message(RegistrationStates.media, F.photo | F.video)
async def set_media(message: types.Message, state: FSMContext):
    media = await state.get_value("media")
    if media and len(media) >= 3:
        await message.answer(_("You can upload at most 3 images/videos"))
        return await finish_registration(message, state)

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

    media = media or []
    media.append(file)
    await state.update_data(media=media)

    if len(media) < 3:
        file_type: str = file["file_type"].name
        msg = _("{media_type} has been uploaded. Upload more photos if you want or press \"Continue\"").format(
            media_type=file_type.capitalize())
        await message.answer(msg, reply_markup=make_keyboard([[_("Continue")]]))
    else:
        await finish_registration(message, state)


async def finish_registration(message: types.Message, state: FSMContext):
    user = await save_user(message, state)
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale})
    await message.answer(_("Registration has been completed!"),
                         reply_markup=get_menu_keyboard())

    profile = await get_profile_card(user)
    await message.answer_media_group(profile)
    await state.set_state(MenuStates.menu)


async def save_user(message: types.Message, state: FSMContext):
    assert message.from_user
    data = await state.get_data()
    media = [FileAddDTO.model_validate(m) for m in data["media"]]

    preferences = PreferenceAddDTO(
        min_age=data["preferred_min_age"],
        max_age=data["preferred_max_age"],
        preferred_gender=data["preferred_gender"]
    )

    if "testing" in data and data["testing"]:
        # TODO: remove after testing
        telegram_id = randint(1000000000, 9999999999)
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
        await session.commit()

    return user_db
