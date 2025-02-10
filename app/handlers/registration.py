from random import randint

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy.exc import NoResultFound

from app.core.db import session_factory
from app.dto.file import FileAddDTO
from app.dto.user import PlaceAddDTO, PreferenceAddDTO, UserRelAddDTO
from app.enums import FileTypes
from app.filters import IsHuman
from app.geocoding import get_place_id
from app.handlers.menu import activate_account_start, show_menu
from app.keyboards import (GENDER_PREFERENCES, GENDERS, LANGUAGES,
                           get_ask_location_keyboard,
                           get_ask_phone_number_keyboard, get_genders_keyboard,
                           get_languages_keyboard, get_menu_keyboard,
                           get_preferred_genders_keyboard, make_keyboard)
from app.middlewares import i18n_middleware
from app.models.user import Place
from app.queries import get_user
from app.states import AppStates
from app.utils import get_profile_card
from app.validators import (Params, validate_bio, validate_birth_date,
                            validate_media_size, validate_name,
                            validate_preference_age_string,
                            validate_video_duration)

router = Router()
router.message.filter(IsHuman())


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        _(
            "Hi there! I'm a bot to help you find your soulmate.\n\n"
            ""
            "Here's how it works: you'll be shown profiles of other users, and you can like or dislike them. "
            "When you like a profile, we will notify the user about it. If the user likes you back, you'll be matched "
            "and can start chatting.\n\n"
            ""
            "If you have any questions, contact our <a href='{support_link}'>support team</a>."
        ).format(support_link="https://t.me/anordatingsupportbot"),
        parse_mode="HTML",
    )


@router.message(AppStates.deleted, F.text == __("Start registration"))
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    assert message.from_user
    await state.set_state(None)
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale})

    try:
        user = await get_user(telegram_id=message.from_user.id, with_media=True)
        await i18n_middleware.set_locale(state, user.ui_language.name)
        await state.set_data({"locale": user.ui_language.name})

        if user.is_active:
            await show_menu(message, state)
        else:
            await activate_account_start(message, state)
    except NoResultFound:
        await set_language_start(message, state)


async def set_language_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Hi! Please select a language"), reply_markup=get_languages_keyboard()
    )
    await state.set_state(AppStates.set_ui_language)


@router.message(AppStates.set_ui_language, F.text.in_(LANGUAGES.keys()))
async def set_language(message: types.Message, state: FSMContext):
    assert message.text
    language = LANGUAGES[message.text]

    await i18n_middleware.set_locale(state, language.name)
    await state.update_data({"language": language})

    await set_name_start(message, state)


@router.message(AppStates.set_ui_language)
async def set_language_invalid(message: types.Message, state: FSMContext):
    await message.answer(
        _("Please select one of the given languages"),
        reply_markup=get_languages_keyboard(),
    )


async def set_name_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("What is your name?"), reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AppStates.set_name)


@router.message(AppStates.set_name, F.text)
async def set_name(message: types.Message, state: FSMContext):
    assert message.text

    try:
        validate_name(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    await state.update_data(name=message.text)
    await set_birth_date_start(message, state)


async def set_birth_date_start(message: types.Message, state: FSMContext):
    msg = _(
        "What's your birth date? Use one these formats:"
        "\n"
        "\n<b>YYYY-MM-DD</b> (For example, 2000-12-31)"
        "\n<b>DD.MM.YYYY</b> (For example, 31.12.2000)"
        "\n<b>MM/DD/YYYY</b> (For example, 12/31/2000)"
    )
    await message.answer(msg, parse_mode="HTML")
    await state.set_state(AppStates.set_birth_date)


@router.message(AppStates.set_birth_date, F.text)
async def set_birth_date(message: types.Message, state: FSMContext):
    assert message.text

    try:
        validate_birth_date(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    await state.update_data(birth_date=message.text)
    await set_gender_start(message, state)


async def set_gender_start(message: types.Message, state: FSMContext):
    await message.answer(_("What is your gender?"), reply_markup=get_genders_keyboard())
    await state.set_state(AppStates.set_gender)


@router.message(AppStates.set_gender, F.text.in_([x[0] for x in GENDERS]))
async def set_gender(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    gender = None
    for k, v in GENDERS:
        if k == message.text:
            gender = v
            break

    await state.update_data(gender=gender)
    await set_bio_start(message, state)


@router.message(AppStates.set_gender)
async def set_gender_invalid(message: types.Message):
    await message.answer(_("Please select one of the given options"))


async def set_bio_start(message: types.Message, state: FSMContext):
    msg = _("Tell us more about yourself. What are your hobbies, interests, etc.?")
    await message.answer(msg, reply_markup=make_keyboard([[_("Skip")]]))
    await state.set_state(AppStates.set_bio)


@router.message(AppStates.set_bio, F.text == __("Skip"))
async def skip_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=None)
    await set_preferred_gender_start(message, state)


@router.message(AppStates.set_bio, F.text)
async def set_bio(message: types.Message, state: FSMContext):
    try:
        validate_bio(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    await state.update_data(bio=message.text)
    await set_preferred_gender_start(message, state)


async def set_preferred_gender_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Who are you looking for?"), reply_markup=get_preferred_genders_keyboard()
    )
    await state.set_state(AppStates.set_gender_preferences)


@router.message(
    AppStates.set_gender_preferences, F.text.in_([x[0] for x in GENDER_PREFERENCES])
)
async def set_preferred_gender(message: types.Message, state: FSMContext):
    preferred_gender = None
    for k, v in GENDER_PREFERENCES:
        if k == message.text:
            preferred_gender = v
            break
    assert preferred_gender

    await state.update_data(preferred_gender=preferred_gender)
    await set_age_preferences_start(message, state)


@router.message(AppStates.set_gender_preferences, F.text)
async def set_gender_preferences_invalid(message: types.Message):
    await message.answer(
        _("Please select one of the given options"),
        reply_markup=get_preferred_genders_keyboard(),
    )


async def set_age_preferences_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("What is your preferred age range? (e.g. 18-25)"),
        reply_markup=make_keyboard([[_("Skip")]]),
    )
    await state.set_state(AppStates.set_age_preferences)


@router.message(AppStates.set_age_preferences, F.text == __("Skip"))
async def skip_age_preferences(message: types.Message, state: FSMContext):
    await state.update_data(preferred_min_age=None)
    await state.update_data(preferred_max_age=None)
    await set_location_start(message, state)


@router.message(AppStates.set_age_preferences, F.text)
async def set_age_preferences(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    try:
        min_age, max_age = validate_preference_age_string(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    await state.update_data(preferred_min_age=min_age)
    await state.update_data(preferred_max_age=max_age)
    await set_location_start(message, state)


async def set_location_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Please share your location"), reply_markup=get_ask_location_keyboard()
    )
    await state.set_state(AppStates.set_location)


@router.message(AppStates.set_location, F.location)
async def set_location(message: types.Message, state: FSMContext):
    assert message.location and message.from_user

    lat, lng = message.location.latitude, message.location.longitude
    await state.update_data(latitude=lat)
    await state.update_data(longitude=lng)

    place_id = get_place_id(lat, lng)
    await state.update_data(place_id=place_id)

    await set_media_start(message, state)


@router.message(AppStates.set_location)
async def set_location_invalid(message: types.Message):
    await message.answer(
        _("Please share your location by clicking the button below"),
        reply_markup=get_ask_location_keyboard(),
    )


async def set_media_start(message: types.Message, state: FSMContext):
    await message.answer(
        _(
            "Please upload photos or videos of yourself ({min_media_count}-{max_media_count})"
        ).format(
            min_media_count=Params.media_min_count,
            max_media_count=Params.media_max_count,
        ),
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AppStates.set_media)


@router.message(AppStates.set_media, F.text == __("Continue"))
async def continue_registration(message: types.Message, state: FSMContext):
    media = await state.get_value("media")
    try:
        validate_media_size(media or [])
    except ValueError as e:
        return await message.answer(str(e))
    await set_phone_number_start(message, state)


@router.message(AppStates.set_media, F.photo | F.video)
async def set_media(message: types.Message, state: FSMContext):
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
        try:
            thumbnail = None
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
                "duration": validate_video_duration(message.video.duration),
                "file_size": message.video.file_size,
                "mime_type": message.video.mime_type,
                "thumbnail": thumbnail,
            }
        except ValueError as e:
            return await message.answer(str(e))

    assert file is not None

    media = (await state.get_value("media")) or []
    media.append(file)
    await state.update_data(media=media)

    try:
        validate_media_size(media)
    except ValueError as e:
        await message.answer(str(e))
        return await set_phone_number_start(message, state)

    if len(media) >= Params.media_max_count:
        await message.answer(_("File has been uploaded"))
        return await set_phone_number_start(message, state)

    msg = _(
        'File has been uploaded. Upload more media files if you want or press "Continue"'
    )
    await message.answer(msg, reply_markup=make_keyboard([[_("Continue")]]))


async def set_phone_number_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Please share your phone number"),
        reply_markup=get_ask_phone_number_keyboard(),
    )
    await state.set_state(AppStates.set_phone_number)


@router.message(AppStates.set_phone_number, F.contact)
async def set_phone_number(message: types.Message, state: FSMContext):
    assert message.contact and message.from_user

    if not message.contact.user_id == message.from_user.id:
        return await message.answer(_("Please share your own phone number"))

    phone_number = message.contact.phone_number
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    await state.update_data(phone_number=phone_number)
    await finish_registration(message, state)


@router.message(AppStates.set_phone_number)
async def set_phone_number_invalid(message: types.Message):
    await message.answer(
        _("Please share your phone number by clicking the button below")
    )


async def finish_registration(message: types.Message, state: FSMContext):
    assert message.from_user
    data = await state.get_data()
    media = [FileAddDTO.model_validate(m) for m in data["media"]]

    preferences = PreferenceAddDTO(
        min_age=data["preferred_min_age"],
        max_age=data["preferred_max_age"],
        preferred_gender=data["preferred_gender"],
    )

    if "testing" in data and data["testing"]:
        # TODO: remove after testing
        telegram_id = randint(1000000000, 9999999999)
    else:
        telegram_id = message.from_user.id

    user = UserRelAddDTO(
        telegram_id=telegram_id,
        name=data["name"],
        birth_date=data["birth_date"],
        bio=data["bio"],
        gender=data["gender"],
        ui_language=data["language"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        phone_number=data["phone_number"],
        media=media,
        preferences=preferences,
        place=PlaceAddDTO(id=data["place_id"]) if data["place_id"] else None,
    )

    user_db = user.to_orm()
    async with session_factory() as session:
        session.add(user_db)
        await session.commit()

    await message.answer(
        _("Registration has been completed!"), reply_markup=get_menu_keyboard()
    )
    profile = await get_profile_card(user_db)
    await message.answer_media_group(profile)
    await show_menu(message, state)
