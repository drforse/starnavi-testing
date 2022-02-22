from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import BaseModelBase, ModelBase
from ..sa_models import LikeModel


class LikeBase(BaseModelBase):
    """it is used on <User>.liked and <Post>.likes"""
    __sa_model__ = LikeModel
    __relationship_fields__ = {"user", "post"}

    user_id: int
    post_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: 'Optional[User]' = None
    post: 'Optional[Post]' = None


class Like(LikeBase, ModelBase):
    id: int


class LikeCreate(LikeBase):
    pass


from .post import Post  # noqa
from .user import User  # noqa
LikeBase.update_forward_refs(**locals())
Like.update_forward_refs(**locals())
LikeCreate.update_forward_refs(**locals())
