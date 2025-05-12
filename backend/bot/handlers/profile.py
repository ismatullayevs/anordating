from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from shared.core.db import session_factory
from shared.dto.file import FileAddDTO
from shared.enums import FileTypes, UILanguages
from bot.filters import IsActiveHumanUser, IsHuman
from shared.geocoding import get_place, get_place_id, get_places
from bot.handlers.menu import show_settings
from bot.handlers.registration import GENDER_PREFERENCES, GENDERS
from bot.keyboards import (
    CLEAR_TXT,
    get_ask_location_keyboard,
    get_ask_phone_number_keyboard,
    get_genders_keyboard,
    get_preferences_update_keyboard,
    get_preferred_genders_keyboard,
    get_profile_update_keyboard,
    make_keyboard,
)
from shared.models.user import Place, PlaceName, Preferences, User
from shared.queries import get_user
from bot.states import AppStates
from bot.utils import clear_state, get_profile_card
from shared.validators import (
    Params,
    validate_bio,
    validate_birth_date,
    validate_media_size,
    validate_name,
    validate_preference_age_string,
    validate_video_duration,
)

router = Router()
router.message.filter(IsHuman())


@router.message(
    AppStates.settings,
    F.text == __("👤 My profile"),
    IsActiveHumanUser(with_media=True),
)
async def show_profile(message: types.Message, state: FSMContext, user: User):
    profile = await get_profile_card(user)
    await message.answer_media_group(profile)

    await message.answer(
        _("Press the buttons below to update your profile"),
        reply_markup=get_profile_update_keyboard(),
    )
    await state.set_state(AppStates.profile)
    await clear_state(state, except_locale=True)


@router.message(AppStates.settings, F.text == __("🔎 Search settings"))
async def update_preferences(
    message: types.Message, state: FSMContext, with_keyboard: bool = True
):
    if with_keyboard:
        await message.answer(
            _("Search settings"), reply_markup=get_preferences_update_keyboard()
        )
    await state.set_state(AppStates.preferences)
    await clear_state(state, except_locale=True)


@router.message(AppStates.profile, F.text == __("⬅️ Back"))
@router.message(AppStates.preferences, F.text == __("⬅️ Back"))
async def back_to_settings(message: types.Message, state: FSMContext):
    await show_settings(message, state)


@router.message(AppStates.profile, F.text == __("✏️ Name"))
async def update_name_start(message: types.Message, state: FSMContext):
    await message.answer(_("Enter your name"), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AppStates.update_name)


@router.message(AppStates.update_name, F.text)
async def update_name(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    try:
        name = validate_name(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    async with session_factory() as session:
        query = (
            update(User)
            .where(User.telegram_id == message.from_user.id)
            .values(name=name)
            .returning(User)
            .options(selectinload(User.media))
        )

        user = (await session.execute(query)).scalar_one()
        await session.commit()

    await message.answer(_("Your profile has been updated"))
    await show_profile(message, state, user)


@router.message(AppStates.profile, F.text == __("🔢 Birth date"))
async def update_birth_date_start(message: types.Message, state: FSMContext):
    msg = _(
        "What's your birth date? Use one these formats:"
        "\n"
        "\n<b>YYYY-MM-DD</b> (For example, 2000-12-31)"
        "\n<b>DD.MM.YYYY</b> (For example, 31.12.2000)"
        "\n<b>MM/DD/YYYY</b> (For example, 12/31/2000)"
    )
    await message.answer(
        msg, reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML"
    )
    await state.set_state(AppStates.update_age)


@router.message(AppStates.update_age, F.text)
async def update_birth_date(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    try:
        birth_date = validate_birth_date(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    async with session_factory() as session:
        query = (
            update(User)
            .where(User.telegram_id == message.from_user.id)
            .values(birth_date=birth_date)
            .returning(User)
            .options(selectinload(User.media))
        )
        user = (await session.execute(query)).scalar_one()
        await session.commit()

    await message.answer(_("Your profile has been updated"))
    await show_profile(message, state, user)


@router.message(AppStates.profile, F.text == __("👫 Gender"))
async def update_gender_start(message: types.Message, state: FSMContext):
    await message.answer(_("Select your gender"), reply_markup=get_genders_keyboard())
    await state.set_state(AppStates.update_gender)


@router.message(AppStates.update_gender, F.text.in_([x[0] for x in GENDERS]))
async def update_gender(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    gender = None
    for k, v in GENDERS:
        if k == message.text:
            gender = v
            break

    async with session_factory() as session:
        query = (
            update(User)
            .where(User.telegram_id == message.from_user.id)
            .values(gender=gender)
            .returning(User)
            .options(selectinload(User.media))
        )
        user = (await session.execute(query)).scalar_one()
        await session.commit()

    await message.answer(_("Your profile has been updated"))
    await show_profile(message, state, user)


@router.message(AppStates.profile, F.text == __("📝 Bio"))
async def update_bio_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Tell us more about yourself. What are your hobbies, interests, etc.?"),
        reply_markup=make_keyboard([[CLEAR_TXT]]),
    )
    await state.set_state(AppStates.update_bio)


@router.message(AppStates.update_bio, F.text)
async def update_bio(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    bio = message.text
    if bio == CLEAR_TXT:
        bio = None
    try:
        bio = validate_bio(bio)
    except ValueError as e:
        return await message.answer(str(e))

    async with session_factory() as session:
        query = (
            update(User)
            .where(User.telegram_id == message.from_user.id)
            .values(bio=bio)
            .returning(User)
            .options(selectinload(User.media))
        )
        user = (await session.execute(query)).scalar_one()
        await session.commit()

    await message.answer(_("Your profile has been updated"))
    await show_profile(message, state, user)


@router.message(AppStates.preferences, F.text == __("👩‍❤️‍👨 Gender preferences"))
async def update_gender_preferences_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Who are you looking for?"), reply_markup=get_preferred_genders_keyboard()
    )
    await state.set_state(AppStates.update_gender_preferences)


@router.message(
    AppStates.update_gender_preferences, F.text.in_([x[0] for x in GENDER_PREFERENCES])
)
async def update_gender_preferences(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    preferred_gender = None
    for k, v in GENDER_PREFERENCES:
        if k == message.text:
            preferred_gender = v
            break

    async with session_factory() as session:
        query = (
            update(Preferences)
            .where(Preferences.user_id == User.id)
            .where(User.telegram_id == message.from_user.id)
            .values(preferred_gender=preferred_gender)
        )
        await session.execute(query)
        await session.commit()

    await message.answer(
        _("Search settings have been updated"),
        reply_markup=get_preferences_update_keyboard(),
    )
    await update_preferences(message, state, with_keyboard=False)


@router.message(AppStates.preferences, F.text == __("🔢 Age preferences"))
async def update_age_preferences_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("What is your preferred age range? (e.g. 18-25)"),
        reply_markup=make_keyboard([[CLEAR_TXT]]),
    )
    await state.set_state(AppStates.update_age_preferences)


@router.message(AppStates.update_age_preferences, F.text)
async def update_age_preferences(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    if message.text == CLEAR_TXT:
        min_age, max_age = None, None
    else:
        try:
            min_age, max_age = validate_preference_age_string(message.text)
        except ValueError as e:
            return await message.answer(str(e))

    async with session_factory() as session:
        query = (
            update(Preferences)
            .where(Preferences.user_id == User.id)
            .where(User.telegram_id == message.from_user.id)
            .values(min_age=min_age, max_age=max_age)
        )
        await session.execute(query)
        await session.commit()

    await message.answer(
        _("Search settings have been updated"),
        reply_markup=get_preferences_update_keyboard(),
    )
    await update_preferences(message, state, with_keyboard=False)


@router.message(AppStates.profile, F.text == __("📍 Location"))
async def update_location_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Send your location or type the name of your city"),
        reply_markup=get_ask_location_keyboard(),
    )
    await state.set_state(AppStates.update_location)


@router.message(AppStates.update_location, F.text)
async def update_location_by_name(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    language = await state.get_value("locale") or "en"
    assert language
    cities = get_places(message.text, UILanguages[language])
    if not cities:
        return await message.answer(_("City not found"))

    msg = _("Please select your city")
    builder = InlineKeyboardBuilder()
    for city, place_id in cities:
        builder.row(
            types.InlineKeyboardButton(text=city, callback_data=f"place_id:{place_id}")
        )

    await message.answer(msg, reply_markup=builder.as_markup())


@router.callback_query(AppStates.update_location, F.data.startswith("place_id:"))
async def set_location_by_name_selected(
    callback: types.CallbackQuery, state: FSMContext
):
    assert callback.data and isinstance(callback.message, types.Message)

    place_id = callback.data.split(":")[1]
    latitude, longitude, city_name = get_place(place_id, UILanguages.en)

    async with session_factory() as session:
        if place_id:
            query = (
                insert(Place)
                .values(id=place_id)
                .on_conflict_do_nothing(index_elements=["id"])
            )
            await session.execute(query)
            query = (
                insert(PlaceName)
                .values(place_id=place_id, language=UILanguages.en, name=city_name)
                .on_conflict_do_nothing(index_elements=["place_id", "language"])
            )
            await session.execute(query)

        query = (
            update(User)
            .where(User.telegram_id == callback.from_user.id)
            .values(
                latitude=latitude,
                longitude=longitude,
                place_id=place_id,
                is_location_precise=False,
            )
            .returning(User)
            .options(selectinload(User.media))
        )
        user = (await session.execute(query)).scalar_one()
        await session.commit()

    await callback.message.answer(_("Your profile has been updated"))
    await show_profile(callback.message, state, user)

    await callback.message.delete()


@router.message(AppStates.update_location, F.location)
async def update_location(message: types.Message, state: FSMContext):
    assert message.location and message.from_user

    latitude = message.location.latitude
    longitude = message.location.longitude
    place_id = get_place_id(latitude, longitude)

    async with session_factory() as session:
        if place_id:
            query = (
                insert(Place)
                .values(id=place_id)
                .on_conflict_do_nothing(index_elements=["id"])
            )
            await session.execute(query)

        query = (
            update(User)
            .where(User.telegram_id == message.from_user.id)
            .values(
                latitude=latitude,
                longitude=longitude,
                place_id=place_id,
                is_location_precise=True,
            )
            .returning(User)
            .options(selectinload(User.media))
        )
        user = (await session.execute(query)).scalar_one()
        await session.commit()

    await message.answer(_("Your profile has been updated"))
    await show_profile(message, state, user)


@router.message(AppStates.profile, F.text == __("📷 Media"))
async def update_media_start(message: types.Message, state: FSMContext):
    await message.answer(
        _(
            "Please upload photos or videos of yourself ({min_media_count}-{max_media_count})"
        ).format(
            min_media_count=Params.media_min_count,
            max_media_count=Params.media_max_count,
        ),
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AppStates.update_media)


@router.message(AppStates.update_media, F.text == __("Continue"))
async def continue_media(message: types.Message, state: FSMContext):
    media = await state.get_value("media")
    if not media:
        await message.answer(_("Please upload at least one photo"))
        return

    await update_media_finish(message, state)


@router.message(AppStates.update_media, F.photo | F.video)
async def update_media(message: types.Message, state: FSMContext):
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
        return await update_media_finish(message, state)

    if len(media) >= Params.media_max_count:
        await message.answer(_("File has been uploaded"))
        return await update_media_finish(message, state)

    msg = _(
        'File has been uploaded. Upload more media files if you want or press "Continue"'
    )
    await message.answer(msg, reply_markup=make_keyboard([[_("Continue")]]))


async def update_media_finish(message: types.Message, state: FSMContext):
    assert message.from_user
    data = await state.get_data()

    media = [FileAddDTO.model_validate(m).to_orm() for m in data["media"]]
    user = await get_user(
        telegram_id=message.from_user.id, with_media=True, is_active=True
    )

    async with session_factory() as session:
        session.add(user)
        user.media = media
        await session.commit()

    await message.answer(_("Your profile has been updated"))
    await show_profile(message, state, user)


@router.message(AppStates.profile, F.text == __("📞 Phone number"))
async def update_phone_number_start(message: types.Message, state: FSMContext):
    await message.answer(
        _("Please share your phone number"),
        reply_markup=get_ask_phone_number_keyboard(),
    )
    await state.set_state(AppStates.update_phone_number)


@router.message(AppStates.update_phone_number, F.contact)
async def update_phone_number(message: types.Message, state: FSMContext):
    assert message.contact and message.from_user

    if not message.contact.user_id == message.from_user.id:
        return await message.answer(_("Please share your own phone number"))

    phone_number = message.contact.phone_number
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number

    async with session_factory() as session:
        query = (
            update(User)
            .where(User.telegram_id == message.from_user.id)
            .values(phone_number=phone_number)
            .returning(User)
            .options(selectinload(User.media))
        )
        user = (await session.execute(query)).scalar_one()
        await session.commit()

    await message.answer(_("Your profile has been updated"))
    await show_profile(message, state, user)
