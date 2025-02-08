from pydantic import BaseModel
from app.models.base import Base
from typing import Type


class BaseModelWithOrm[T: Base](BaseModel):
    @property
    def orm_model(self) -> Type[T]:
        raise NotImplementedError

    def to_orm(self):
        parsed_schema = dict(self)
        for key, value in parsed_schema.items():
            if isinstance(value, list) and len(value):
                lst = []
                for v in value:
                    if isinstance(v, BaseModelWithOrm):
                        lst.append(v.to_orm())
                    else:
                        lst.append(v)
                parsed_schema[key] = lst
            else:
                if isinstance(value, BaseModelWithOrm):
                    parsed_schema[key] = value.to_orm()

        try:
            return self.orm_model(**parsed_schema)
        except AttributeError:
            raise AttributeError(
                f"Schema {self} doesn't have a Meta.orm_model attribute"
            )
