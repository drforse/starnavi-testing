import abc
import datetime
from typing import Any, Union, TYPE_CHECKING

from pydantic import BaseModel as PydanticModel, SecretStr, SecretBytes
from sqlalchemy.orm import DeclarativeMeta

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny, DictStrAny


class BaseModelBase(abc.ABC, PydanticModel):
    """base model for base models, for ex.: for UserBase"""
    __relationship_fields__: set[str] = set()
    __sa_model__: DeclarativeMeta

    class Config:
        # use_enum_values = True
        orm_mode = True
        validate_assignment = True
        json_encoders = {datetime.datetime: lambda dt: int(dt.timestamp())}

    def dict(
        self,
        *,
        include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        show_secrets: bool = False
    ) -> 'DictStrAny':
        result = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if show_secrets is True:
            for k, v in result.items():
                if isinstance(v, (SecretStr, SecretBytes)):
                    result[k] = v.get_secret_value()
        return result


class ModelBase(abc.ABC):
    """
    base model for complete models as in db
    Create models (like UserCreate) should not be inherited from this
    """
    id: Any
