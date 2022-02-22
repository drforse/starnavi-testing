from .base import MySqlBaseRepository
from ...models import User, UserCreate


class UsersRepository(MySqlBaseRepository[User, UserCreate]):
    pass
