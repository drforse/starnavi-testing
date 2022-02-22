from datetime import datetime
from typing import Optional

from fastapi import Form
from pydantic import Field, SecretStr

from .base import BaseSchema

__all__ = ("UserSchema", "UserCreateSchema")


class UserSchema(BaseSchema):
    id: int
    username: str
    last_request_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None


class UserCreateSchema(BaseSchema):
    username: str
    password: SecretStr

    @classmethod
    def as_form(
            cls,
            username: str = Form(...),
            password: str = Form(...)
    ) -> 'UserCreateSchema':
        return cls(username=username, password=password)
