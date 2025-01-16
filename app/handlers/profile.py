from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.core.db import session_factory
from app.dto.file import FileAddDTO
from app.enums import FileTypes
from app.handlers.registration import GENDER_PREFERENCES, GENDERS
from app.keyboards import get_ask_location_keyboard, get_profile_update_keyboard, make_keyboard
from app.states import ProfileStates, MenuStates
from app.utils import get_profile_card, get_user
from app.models.user import Preferences, User
from sqlalchemy import exc, update


router = Router()


@router.message(MenuStates.menu, F.text == __("👤 My profile"))
async def show_profile(message: types.Message, state: FSMContext):
    assert message.from_user

    try:
        user = await get_user(telegram_id=message.from_user.id, with_media=True)
    except exc.NoResultFound:
        return await message.answer(_("You need to create a profile first"))

    profile = await get_profile_card(user)
    await message.answer_media_group(profile)

    await message.answer(_("Press the buttons below to update your profile"),
                         reply_markup=get_profile_update_keyboard())
    await state.set_state(ProfileStates.profile)
    locale = await state.get_value("locale")
    await state.set_data({"locale": locale})


@router.message(ProfileStates.profile, F.text == __("✏️ Name"))
async def update_name_start(message: types.Message, state: FSMContext):
    await message.answer(_("Enter your name"), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.name)


@router.message(ProfileStates.name, F.text)
async def update_name(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    if len(message.text) < 3:
        return await message.answer(_("Name must be at least 3 characters long"))
    elif len(message.text) > 30:
        return await message.answer(_("Name must be less than 30 characters"))

    if not all(x.isalpha() or x.isspace() for x in message.text):
        return await message.answer(_("Name can only contain letters"))

    async with session_factory() as session:
        query = update(User).where(User.telegram_id ==
                                   message.from_user.id).values(name=message.text)
        await session.execute(query)
        await session.commit()

    await show_profile(message, state)


@router.message(ProfileStates.profile, F.text == __("🔢 Age"))
async def update_age_start(message: types.Message, state: FSMContext):
    await message.answer(_("Enter your age"), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.age)


@router.message(ProfileStates.age, F.text)
async def update_age(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    try:
        age = int(message.text)
    except ValueError:
        return await message.answer(_("Please enter a number"))

    if age < 18:
        return await message.answer(_("You must be at least 18 years old to use this bot"))
    elif age > 100:
        return await message.answer(_("You must be less than 100 years old to use this bot"))

    async with session_factory() as session:
        query = update(User).where(User.telegram_id ==
                                   message.from_user.id).values(age=int(message.text))
        await session.execute(query)
        await session.commit()

    await show_profile(message, state)


@router.message(ProfileStates.profile, F.text == __("👫 Gender"))
async def update_gender_start(message: types.Message, state: FSMContext):
    buttons = [[str(x[0]) for x in GENDERS]]
    await message.answer(_("Select your gender"), reply_markup=make_keyboard(buttons))
    await state.set_state(ProfileStates.gender)


@router.message(ProfileStates.gender, F.text.in_([x[0] for x in GENDERS]))
async def update_gender(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    gender = None
    for k, v in GENDERS:
        if k == message.text:
            gender = v
            break
    if not gender:
        return await message.answer(_("Please select one of the options"))

    async with session_factory() as session:
        query = update(User).where(User.telegram_id ==
                                   message.from_user.id).values(gender=gender)
        await session.execute(query)
        await session.commit()

    await show_profile(message, state)


@router.message(ProfileStates.profile, F.text == __("📝 Bio"))
async def update_bio_start(message: types.Message, state: FSMContext):
    await message.answer(_("Tell us more about yourself. Who are you looking for?"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.bio)


@router.message(ProfileStates.bio, F.text)
async def update_bio(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    if len(message.text) > 255:
        await message.answer(_("Bio must be less than 255 characters"))
        return

    async with session_factory() as session:
        query = update(User).where(User.telegram_id ==
                                   message.from_user.id).values(bio=message.text)
        await session.execute(query)
        await session.commit()

    await show_profile(message, state)


@router.message(ProfileStates.profile, F.text == __("👩‍❤️‍👨 Gender preferences"))
async def update_gender_preferences_start(message: types.Message, state: FSMContext):
    buttons = [[str(x[0]) for x in GENDER_PREFERENCES]]
    await message.answer(_("Select preferred gender"), reply_markup=make_keyboard(buttons))
    await state.set_state(ProfileStates.gender_preferences)


@router.message(ProfileStates.gender_preferences, F.text.in_([x[0] for x in GENDER_PREFERENCES]))
async def update_gender_preferences(message: types.Message, state: FSMContext):
    assert message.text and message.from_user
    preferred_gender = None
    for k, v in GENDER_PREFERENCES:
        if k == message.text:
            preferred_gender = v
            break
    if not preferred_gender:
        return await message.answer(_("Please select one of the options"))

    async with session_factory() as session:
        query = (
            update(Preferences)
            .where(Preferences.user_id == User.id)
            .where(User.telegram_id == message.from_user.id)
            .values(preferred_gender=preferred_gender)
            .execution_options(synchronize_session=False)
        )
        await session.execute(query)
        await session.commit()

    await show_profile(message, state)


@router.message(ProfileStates.profile, F.text == __("🔢 Age preferences"))
async def update_age_preferences_start(message: types.Message, state: FSMContext):
    await message.answer(_("Enter preferred age range"), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.age_preferences)


@router.message(ProfileStates.age_preferences, F.text)
async def update_age_preferences(message: types.Message, state: FSMContext):
    assert message.text and message.from_user

    try:
        min_age, max_age = map(int, message.text.split("-"))
    except ValueError:
        return await message.answer(_("Please enter a valid age range"))

    if not min_age < max_age:
        return await message.answer(_("Min age must be less than max age"))
    if not 18 <= min_age < max_age <= 100:
        return await message.answer(_("Age range must be between 18 and 100"))

    async with session_factory() as session:
        query = (
            update(Preferences)
            .where(Preferences.user_id == User.id)
            .where(User.telegram_id == message.from_user.id)
            .values(min_age=min_age, max_age=max_age)
            .execution_options(synchronize_session=False)
        )
        await session.execute(query)
        await session.commit()

    await show_profile(message, state)


@router.message(ProfileStates.profile, F.text == __("📍 Location"))
async def update_location_start(message: types.Message, state: FSMContext):
    await message.answer(_("Send your location"), reply_markup=get_ask_location_keyboard())
    await state.set_state(ProfileStates.location)


@router.message(ProfileStates.location, F.location)
async def update_location(message: types.Message, state: FSMContext):
    assert message.location and message.from_user

    async with session_factory() as session:
        query = (update(User)
                 .where(User.telegram_id == message.from_user.id)
                 .values(latitude=message.location.latitude,
                         longitude=message.location.longitude))
        await session.execute(query)
        await session.commit()

    await show_profile(message, state)


@router.message(ProfileStates.profile, F.text == __("📷 Media"))
async def update_media_start(message: types.Message, state: FSMContext):
    await message.answer(_("Please upload photos or videos of yourself"), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.media)


@router.message(ProfileStates.media, F.text == __("Continue"))
async def continue_registration(message: types.Message, state: FSMContext):
    media = await state.get_value("media")
    if not media:
        await message.answer(_("Please upload at least one photo"))
        return

    await update_media_finish(message, state)
    await show_profile(message, state)


@router.message(ProfileStates.media, F.photo | F.video)
async def update_media(message: types.Message, state: FSMContext):
    media = await state.get_value("media")
    if media and len(media) >= 3:
        await message.answer(_("You can upload at most 3 images/videos"))
        return await update_media_finish(message, state)

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
        await update_media_finish(message, state)


async def update_media_finish(message: types.Message, state: FSMContext):
    assert message.from_user
    data = await state.get_data()

    media = [FileAddDTO.model_validate(m).to_orm() for m in data["media"]]
    user = await get_user(telegram_id=message.from_user.id, with_media=True)

    async with session_factory() as session:
        session.add(user)
        user.media = media
        await session.commit()

    await show_profile(message, state)
