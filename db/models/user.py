from datetime import datetime
from typing import Optional

from pydantic import SecretStr, Field

from .base import BaseModelBase, ModelBase
from ..sa_models import UserModel

__all__ = ("User", "UserCreate")


class UserBase(BaseModelBase):
    __relationship_fields__ = {"posts"}
    __sa_model__ = UserModel

    username: str
    password: SecretStr
    last_request_at: datetime = Field(default_factory=datetime.utcnow)

    posts: 'list[Post]' = Field(default_factory=list)


class User(UserBase, ModelBase):
    id: int
    last_login_at: Optional[datetime] = None


class UserCreate(UserBase):
    pass


from .post import Post  # noqa
UserBase.update_forward_refs(**locals())
User.update_forward_refs(**locals())
UserCreate.update_forward_refs(**locals())
