from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Iterable
from aiogram.utils.i18n import gettext as _, lazy_gettext as __


def make_row_keyboard(items: Iterable[str]) -> ReplyKeyboardMarkup:
    """
    Makes a row keyboard with the given items
    :param items: list of items
    :return: ReplyKeyboardMarkup
    """

    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Returns a menu keyboard
    :return: ReplyKeyboardMarkup
    """
    keyboard = [
        [KeyboardButton(text=_("🔎 Search")), KeyboardButton(text=_("👍 Likes"))],
        [KeyboardButton(text=_("👤 My profile")), KeyboardButton(text=_("❤️ Matches"))],
        [KeyboardButton(text=_("⛔️ Deactivate")), KeyboardButton(text=_("⚙️ Settings"))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_search_keyboard() -> ReplyKeyboardMarkup:
    """
    Returns a search keyboard
    :return: ReplyKeyboardMarkup
    """
    keyboard = [
        [KeyboardButton(text=_("⏪")), KeyboardButton(text=_("👎")), KeyboardButton(text=_("👍"))],
        [KeyboardButton(text=_("✍️ Report")), KeyboardButton(text=_("⬅️ Menu"))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_ask_location_keyboard() -> ReplyKeyboardMarkup:
    """
    Returns a keyboard to ask for location
    :return: ReplyKeyboardMarkup
    """
    keyboard = [
        [KeyboardButton(text=_("📍 Send location"), request_location=True)],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)