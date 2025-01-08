from pydantic import BaseModel


def pydantic_to_sqlalchemy(schema: BaseModel):
    parsed_schema = dict(schema)
    for key, value in parsed_schema.items():
        if isinstance(value, list) and len(value):
            lst = []
            for v in value:
                if isinstance(v, BaseModel):
                    lst.append(pydantic_to_sqlalchemy(v))
                else:
                    lst.append(v)
            parsed_schema[key] = lst
        else:
            if isinstance(value, BaseModel):
                parsed_schema[key] = pydantic_to_sqlalchemy(value)

    try:    
        return schema.Meta.orm_model(**parsed_schema) # type: ignore
    except AttributeError:
        raise AttributeError(f"Schema {schema} doesn't have a Meta.orm_model attribute")
