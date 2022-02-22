from .base import MySqlBaseRepository
from ...models import Post, PostCreate


class PostsRepository(MySqlBaseRepository[Post, PostCreate]):
    pass
