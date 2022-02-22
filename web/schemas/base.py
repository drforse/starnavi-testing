import abc
import datetime

from pydantic import BaseModel as PydanticModel


class BaseSchema(abc.ABC, PydanticModel):
    class Config:
        allow_mutation = False
        orm_mode = True
        validate_assignment = True
        json_encoders = {datetime.datetime: lambda dt: int(dt.timestamp())}
