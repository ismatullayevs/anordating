from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel

from app.enums import Genders, UILanguages
from app.validators import validate_bio, validate_name


class UserInSchema(BaseModel):
    telegram_id: int
    name: Annotated[str, AfterValidator(validate_name)]
    birth_date: datetime
    bio: Annotated[str | None, AfterValidator(validate_bio)]
    gender: Genders
    latitude: float
    longitude: float
    ui_language: UILanguages
    is_location_precise: bool
    place_id: str | None = None


class UserSchema(UserInSchema):
    id: UUID
    rating: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_superuser: bool = False

    @property
    def age(self) -> int:
        """Calculates the age of the user based on their birth date."""
        if not self.birth_date:
            return 0
        today = datetime.now()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )
