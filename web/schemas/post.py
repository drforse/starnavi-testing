from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import BaseSchema

__all__ = ("PostSchema", "PostCreateSchema")


class PostSchema(BaseSchema):
    id: int
    created_at: datetime
    user_id: int
    text: str
    user: Optional['UserSchema']
    # NOTE: I would prefer to make 'user' field - optional and add user_id field, but it's simplified


class PostCreateSchema(BaseSchema):
    text: str = Field(max_length=65535)


from .user import UserSchema  # noqa
PostSchema.update_forward_refs(**locals())
