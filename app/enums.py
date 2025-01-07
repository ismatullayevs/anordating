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


class ReactionType(Enum):
    like = "like"
    dislike = "dislike"


class ReportStatusTypes(Enum):
    pending = "pending"
    reviewing = "reviewing"
    pending_info = "pending_info"
    valid = "valid"
    invalid = "invalid"
    resolved = "resolved"
    closed = "closed"
