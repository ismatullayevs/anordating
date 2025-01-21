from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    language = State()
    name = State()
    birth_date = State()
    gender = State()
    bio = State()
    gender_preferences = State()
    age_preferences = State()
    location = State()
    media = State()
    phone_number = State()


class MenuStates(StatesGroup):
    menu = State()
    search = State()
    likes = State()
    settings = State()
    language = State()
    matches = State()
    report_reason = State()
    deactivate_confirm = State()
    deactivated = State()
    delete_confirm = State()


class ProfileStates(StatesGroup):
    profile = State()
    name = State()
    age = State()
    gender = State()
    bio = State()
    gender_preferences = State()
    age_preferences = State()
    location = State()
    media = State()
