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
