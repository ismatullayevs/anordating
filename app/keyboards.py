from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from app.enums import UILanguages, Genders, PreferredGenders


LANGUAGES = {
    "Uzbek 🇺🇿": UILanguages.uz,
    "Russian 🇷🇺": UILanguages.ru,
    "English 🇺🇸": UILanguages.en,
}

GENDERS = (
    (__("Male 👨‍🦱"), Genders.male),
    (__("Female 👩‍🦱"), Genders.female),
)

GENDER_PREFERENCES = (
    (__("I'm looking for men 👨‍🦱"), PreferredGenders.male),
    (__("I'm looking for women 👩‍🦱"), PreferredGenders.female),
    (__("I'm looking for friends 👫"), PreferredGenders.friends),
)


def make_keyboard(items: list[list[str]]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=text) for text in row] for row in items]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    items = [[_("🔎 Watch profiles"), _("👍 Likes")],
             [_("❤️ Matches"), _("⚙️ Settings")]]
    return make_keyboard(items)


def get_search_keyboard() -> ReplyKeyboardMarkup:
    items = [["⏪", "👎", "👍"], [_("✍️ Report"), _("⬅️ Menu")]]
    return make_keyboard(items)


def get_matches_keyboard() -> ReplyKeyboardMarkup:
    items = [["⬅️", "👎", "➡️"], [_("✍️ Report"), _("⬅️ Menu")]]
    return make_keyboard(items)


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    items = [[_("🌐 Language"), _("👤 My profile")],
             [_("⛔️ Deactivate"), _("❌ Delete account")],
             [_("⬅️ Menu")]]
    return make_keyboard(items)


def get_likes_keyboard() -> ReplyKeyboardMarkup:
    return get_search_keyboard()


def get_empty_search_keyboard() -> ReplyKeyboardMarkup:
    items = [[_("⏪ Rewind"), _("⬅️ Menu")]]
    return make_keyboard(items)


def get_languages_keyboard():
    return make_keyboard([list(LANGUAGES.keys())])


def get_genders_keyboard():
    return make_keyboard([[str(x[0]) for x in GENDERS]])


def get_preferred_genders_keyboard():
    return make_keyboard([[str(x[0])] for x in GENDER_PREFERENCES])


def get_ask_location_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=_("📍 Send location"), request_location=True)],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_profile_update_keyboard() -> ReplyKeyboardMarkup:
    items = [
        [_("✏️ Name"), _("🔢 Birthdate"), _("👫 Gender"), _("📝 Bio")],
        [_("👩‍❤️‍👨 Gender preferences"), _("🔢 Age preferences")],
        [_("📍 Location"), _("📷 Media"), _("⬅️ Menu")]
    ]
    return make_keyboard(items)
