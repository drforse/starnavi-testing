from datetime import datetime

from sqlalchemy import select, func

from .base import MySqlBaseRepository
from ...models import Like, LikeCreate
from ...sa_models import LikeModel


class LikesRepository(MySqlBaseRepository[Like, LikeCreate]):
    __model__ = Like
    __create_model__ = LikeCreate

    async def count_aggregated_by_date(self, date_from: datetime = None, date_to: datetime = None, **kwargs) -> list[Like]:
        query = select([func.count()]).select_from(self.__sa_model__).filter_by(**kwargs)
        if date_from is not None:
            query = query.filter(LikeModel.created_at >= date_from)
        if date_to is not None:
            query = query.filter(LikeModel.created_at <= date_to)
        query = self._query(query)
        async with self.session() as s:
            return await s.scalar(query)
