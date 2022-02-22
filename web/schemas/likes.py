from web.schemas.base import BaseSchema


class LikesSchema(BaseSchema):
    all_likes_count: int
    user_likes_count: int
