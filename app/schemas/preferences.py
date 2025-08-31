from uuid import UUID

from pydantic import BaseModel

from app.enums import PreferredGenders


# TODO: add validation
class PreferencesInSchema(BaseModel):
    min_age: int | None = None
    max_age: int | None = None
    preferred_gender: PreferredGenders | None = None


class PreferencesOutSchema(PreferencesInSchema):
    id: int
    user_id: UUID
