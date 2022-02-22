import json
from datetime import datetime

from sqlalchemy import inspect, Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

__all__ = ("Base", "UserModel", "PostModel", "LikeModel")

Base = declarative_base()


class MixinSerializers:
    """should only be used as sa model base"""

    def to_python(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    def as_json(self) -> str:
        return json.dumps(self.to_python())

    def __str__(self):
        return f"<{self.__tablename__}(pk={self.pk})>"  # type: ignore


class UserModel(MixinSerializers, Base):  # type: ignore
    __tablename__ = "user"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(256), unique=True, nullable=False)
    password: str = Column(String(256), nullable=False)
    last_request_at: datetime = Column(DateTime, nullable=False)
    last_login_at: datetime | None = Column(DateTime)

    posts: 'list[PostModel]' = relationship("PostModel", back_populates="user", lazy="noload")
    liked: 'list[LikeModel]' = relationship("LikeModel", back_populates="user", lazy="noload")


class PostModel(MixinSerializers, Base):  # type: ignore
    __tablename__ = "post"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at: datetime = Column(DateTime, nullable=False)
    text: str = Column(Text, nullable=False)

    user: 'UserModel | None' = relationship("UserModel", back_populates="posts", lazy="noload")
    likes: 'list[LikeModel]' = relationship("LikeModel", back_populates="post", lazy="noload", cascade="all, delete")

    def __str__(self):
        return f"<post(pk={self.pk}, user_id={self.user_id}, created_at={self.created_at})>"


class LikeModel(MixinSerializers, Base):  # type: ignore
    __tablename__ = "like"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(ForeignKey("user.id"), primary_key=True)
    post_id: int = Column(ForeignKey("post.id", ondelete="CASCADE"), primary_key=True)

    created_at: datetime = Column(DateTime, nullable=False)

    user: 'UserModel | None' = relationship("UserModel", back_populates="liked", lazy="noload")
    post: 'PostModel | None' = relationship("PostModel", back_populates="likes", lazy="noload")
