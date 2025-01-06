from enum import Enum


class FileTypes(Enum):
    image = "image"
    video = "video"
    audio = "audio"
    document = "document"
    other = "other"


class UILanguages(Enum):
    uz = "uz"
    ru = "ru"
    en = "en"


class Genders(Enum):
    male = "m"
    female = "f"


class PreferredGenders(Enum):
    male = "m"
    female = "f"
    friends = "a"
