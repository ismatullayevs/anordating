from datetime import date, datetime

from aiogram.utils.i18n import gettext as _


class Params:
    name_min_length = 3
    name_max_length = 50

    min_age = 18
    max_age = 100

    bio_max_length = 255

    media_min_count = 1
    media_max_count = 5


def validate_name(value: str) -> str:
    if not (value and all(x.isalpha() or x.isspace() for x in value)):
        raise ValueError(_("Name must only contain letters and spaces"))

    if len(value) < Params.name_min_length:
        raise ValueError(
            _("Name must be at least {min_length} characters long").format(
                min_length=Params.name_min_length
            )
        )
    if len(value) > Params.name_max_length:
        raise ValueError(
            _("Name must be less than {max_length} characters long").format(
                max_length=Params.name_max_length
            )
        )
    return value


def validate_birth_date(value: str) -> datetime:
    """
    Parse a date string and validate that the person is between given age range.

    Supported formats:
    - YYYY-MM-DD (e.g., "1970-10-20")
    - DD.MM.YYYY (e.g., "20.10.1970")
    - MM/DD/YYYY (e.g., "10/20/1970")

    Args:
        value: String containing the date in one of the supported formats

    Returns:
        datetime object representing the parsed date

    Raises:
        ValueError: If the string cannot be parsed into a valid date
                   or if the age is not between given age range
    """
    formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%m/%d/%Y",
    ]

    parsed_date = None
    for date_format in formats:
        try:
            parsed_date = datetime.strptime(value, date_format)
            break
        except ValueError:
            continue

    if parsed_date is None:
        raise ValueError(
            "Invalid date format. Supported formats are: "
            "YYYY-MM-DD (1970-10-20), "
            "DD.MM.YYYY (20.10.1970), "
            "MM/DD/YYYY (10/20/1970)"
        )

    today = date.today()
    age = (
        today.year
        - parsed_date.year
        - ((today.month, today.day) < (parsed_date.month, parsed_date.day))
    )

    if age < Params.min_age:
        raise ValueError(
            "You must be at least {min_age} years old to use this bot".format(
                min_age=Params.min_age
            )
        )
    if age > Params.max_age:
        raise ValueError(
            "You must be less than {max_age} years old to use this bot".format(
                max_age=Params.max_age
            )
        )

    return parsed_date


def validate_bio(value: str | None) -> str | None:
    if value and len(value) > Params.bio_max_length:
        raise ValueError(
            _("Bio must be less than {max_length} characters long").format(
                max_length=Params.bio_max_length
            )
        )
    return value


def validate_media(value: list) -> list:
    if len(value) < Params.media_min_count:
        raise ValueError(
            _("Please upload at least {min_length} media files").format(
                min_length=Params.media_min_count
            )
        )
    if len(value) > Params.media_max_count:
        raise ValueError(
            _("You can upload up to {max_length} media files").format(
                max_length=Params.media_max_count
            )
        )
    return value


def validate_preference_age_string(value: str):
    try:
        min_age, max_age = map(int, value.split("-"))
    except ValueError:
        raise ValueError(_("Please enter a valid age range"))
    min_age = validate_preference_age(min_age)
    max_age = validate_preference_age(max_age)
    min_age, max_age = validate_preference_ages(min_age, max_age)
    return min_age, max_age


def validate_preference_age(value: int | None):
    if value is None:
        return value
    if value < Params.min_age:
        raise ValueError(
            _("Age can't be lower than {min_age}").format(min_age=Params.min_age)
        )
    if value > Params.max_age:
        raise ValueError(
            _("Age can't be higher than {max_age}").format(max_age=Params.max_age)
        )
    return value


def validate_preference_ages(min_age: int | None, max_age: int | None):
    if not min_age or not max_age:
        return (None, None)
    if min_age >= max_age:
        raise ValueError(_("Minimum age needs be to lower than maximum age"))
    return (min_age, max_age)
