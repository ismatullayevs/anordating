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
    male = "male"
    female = "female"


class PreferredGenders(Enum):
    male = "male"
    female = "female"
    friends = "friends"
