from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _, lazy_gettext as __


def make_keyboard(items: list[list[str]]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=text) for text in row] for row in items]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    items = [[_("🔎 Search"), _("👍 Likes")],
             [_("👤 My profile"), _("❤️ Matches")],
             [_("⛔️ Deactivate"), _("⚙️ Settings")]]
    return make_keyboard(items)


def get_search_keyboard() -> ReplyKeyboardMarkup:
    items = [["⏪", "👎", "👍"], [_("✍️ Report"), _("⬅️ Menu")]]
    return make_keyboard(items)


def get_likes_keyboard() -> ReplyKeyboardMarkup:
    return get_search_keyboard()


def get_empty_search_keyboard() -> ReplyKeyboardMarkup:
    items = [[_("⏪ Rewind"), _("⬅️ Menu")]]
    return make_keyboard(items)


def get_ask_location_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=_("📍 Send location"), request_location=True)],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_profile_update_keyboard() -> ReplyKeyboardMarkup:
    items = [
        [_("✏️ Name"), _("🔢 Age"), _("👫 Gender"), _("📝 Bio")],
        [_("👩‍❤️‍👨 Gender preferences"), _("🔢 Age preferences")],
        [_("📍 Location"), _("📷 Media"), _("⬅️ Menu")]
    ]
    return make_keyboard(items)
