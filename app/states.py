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


class MenuStates(StatesGroup):
    menu = State()
    language = State()


class SearchStates(StatesGroup):
    search = State()
    report_reason = State()


class LikesStates(StatesGroup):
    likes = State()


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


class MatchesStates(StatesGroup):
    matches = State()


class DeactivateStates(StatesGroup):
    deactivate_confirm = State()
    deactivated = State()
    

class LanguageStates(StatesGroup):
    language = State()
