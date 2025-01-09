from pydantic_core import PydanticCustomError
from aiogram.utils.i18n import gettext as _
from typing import Any


class NotifyUserError(PydanticCustomError):
    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__('notify_user', message, context) # type: ignore

    def __new__(cls, message: str, context: dict[str, Any] | None = None):
        return super().__new__(cls, 'notify_user', message, context) # type: ignore


def validate_name(name: str):
    min_length = 3
    max_length = 30
    
    if len(name) < min_length:
        err = _("Your name is too short")
        raise NotifyUserError(err)
    
    if len(name) > max_length:
        err = _("Your name is too long")
        raise NotifyUserError(err)

    return name


def validate_age(age: int):
    min_age = 18
    max_age = 100

    if age < min_age:
        err = _("You must be at least {min_age} years old").format(min_age=min_age)
        raise NotifyUserError(err)
    
    if age > max_age:
        err = _("You must be at most {max_age} years old").format(max_age=max_age)
        raise NotifyUserError(err)

    return age


def validate_media_length(media):
    min_media_count = 1
    max_media_count = 3

    if len(media) < min_media_count:
        err = _("You must upload at least {min_media_count} media").format(min_media_count=min_media_count)
        raise NotifyUserError(err)
    
    if len(media) > max_media_count:
        err = _("You can upload at most {max_media_count} media").format(max_media_count=max_media_count)
        raise NotifyUserError(err)
    
    return media