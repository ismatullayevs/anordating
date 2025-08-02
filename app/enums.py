from enum import Enum


class FileTypes(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"
    document = "document"
    other = "other"


class UILanguages(str, Enum):
    uz = "uz"
    ru = "ru"
    en = "en"


class Genders(str, Enum):
    male = "male"
    female = "female"


class PreferredGenders(str, Enum):
    male = "male"
    female = "female"
    both = "both"


class ReactionType(str, Enum):
    like = "like"
    dislike = "dislike"


class ReportStatusTypes(str, Enum):
    pending = "pending"
    reviewing = "reviewing"
    pending_info = "pending_info"
    valid = "valid"
    invalid = "invalid"
    resolved = "resolved"
    closed = "closed"
