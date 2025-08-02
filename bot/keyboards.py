from typing import Iterable

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from babel.support import LazyProxy

# TODO: create a separate enums file for bot
from app.enums import Genders, PreferredGenders, UILanguages

CLEAR_TXT = __("❌ Clear")

LANGUAGES = {
    "Uzbek 🇺🇿": UILanguages.uz,
    "Russian 🇷🇺": UILanguages.ru,
    "English 🇺🇸": UILanguages.en,
}

GENDERS = (
    (__("Male 👨"), Genders.male),
    (__("Female 👩"), Genders.female),
)

GENDER_PREFERENCES = (
    (__("Women 👩"), PreferredGenders.female),
    (__("Men 👨"), PreferredGenders.male),
)


def make_keyboard(
    items: Iterable[Iterable[str | LazyProxy]], placeholder: str | None = None
) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text=text if isinstance(text, str) else text.value)
            for text in row
        ]
        for row in items
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, input_field_placeholder=placeholder
    )


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    items = [[_("🔎 Watch profiles"), _("👍 Likes")], [_("❤️ Matches"), _("⚙️ Settings")]]
    return make_keyboard(items)


def get_search_keyboard() -> ReplyKeyboardMarkup:
    items = [["⏪", "👎", "👍"], [_("✍️ Report"), _("⬅️ Menu")]]
    return make_keyboard(items)


def get_matches_keyboard(has_previous=False, has_next=False) -> ReplyKeyboardMarkup:
    top = ["👎"]
    if has_previous:
        top.insert(0, "⬅️")
    if has_next:
        top.append("➡️")

    items = [top, [_("✍️ Report"), _("⬅️ Menu")]]
    return make_keyboard(items)


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    items = [
        [_("👤 My profile"), _("🔎 Search settings")],
        [_("🌐 Language"), _("⛔️ Deactivate")],
        [_("❌ Delete account"), _("⬅️ Menu")],
    ]
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
    return ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, input_field_placeholder=_("City name")
    )


def get_profile_update_keyboard() -> ReplyKeyboardMarkup:
    items = [
        [_("✏️ Name"), _("🔢 Birth date"), _("👫 Gender")],
        [_("📝 Bio"), _("📍 Location"), _("📷 Media")],
        [_("⬅️ Back")],
    ]
    return make_keyboard(items)


def get_preferences_update_keyboard() -> ReplyKeyboardMarkup:
    items = [[_("👩‍❤️‍👨 Gender preferences"), _("🔢 Age preferences")], [_("⬅️ Back")]]
    return make_keyboard(items)
