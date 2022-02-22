from datetime import datetime
from typing import Optional

from pydantic import Field, constr

from .base import BaseModelBase, ModelBase
from ..sa_models import PostModel

__all__ = ("Post", "PostCreate")


class PostBase(BaseModelBase):
    __relationship_fields__ = {"user", "likes"}
    __sa_model__ = PostModel

    user_id: int = Field(allow_mutation=False)
    created_at: datetime = Field(allow_mutation=False, default_factory=datetime.utcnow)
    text: str = Field(max_length=65535)

    user: 'Optional[User]' = Field(allow_mutation=False)


class Post(PostBase, ModelBase):
    id: int


class PostCreate(PostBase):
    pass


from .user import User  # noqa
PostBase.update_forward_refs(**locals())
Post.update_forward_refs(**locals())
PostCreate.update_forward_refs(**locals())
