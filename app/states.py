from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    language = State()
    name = State()
    age = State()
    gender = State()
    bio = State()
    media = State()
    location = State()
    gender_preferences = State()
    age_preferences = State()


class MenuStates(StatesGroup):
    menu = State()


class SearchStates(StatesGroup):
    search = State()


class LikesStates(StatesGroup):
    likes = State()


class ProfileStates(StatesGroup):
    profile = State()


class MatchesStates(StatesGroup):
    matches = State()


class DeactivateStates(StatesGroup):
    deactivate = State()


class LanguageStates(StatesGroup):
    language = State()
