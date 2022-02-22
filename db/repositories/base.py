import abc
import typing
from typing import Optional
from contextlib import asynccontextmanager
from typing import Generic, TypeVar

from sqlalchemy import select, update, delete, insert, func
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import Update, Insert

from ..sa_loading import add_loading_to_query, DEFAULT_SA_LOADING, QueryType

ModelType = TypeVar("ModelType")
ModelCreateType = TypeVar("ModelCreateType")


class BaseRepositoryGeneric(Generic[ModelType, ModelCreateType]):
    @property
    def __model__(self) -> typing.Type[ModelType]:
        raise NotImplementedError

    @property
    def __create_model__(self) -> typing.Type[ModelCreateType]:
        raise NotImplementedError

    async def get(self, **kwargs) -> Optional[ModelType]: ...
    async def get_or_create(self, **kwargs) -> ModelType: ...
    async def update(self, entity: ModelType) -> Optional[ModelType]: ...
    async def delete(self, entity: ModelType): ...
    async def delete_by_id(self, id: int): ...
    async def create(self, entity: ModelCreateType) -> ModelType: ...
    async def get_many(self, **kwargs) -> list[ModelType]: ...
    async def count(self, **kwargs) -> int: ...
    def resolve_relationships(self, entity: ModelType | ModelCreateType) -> list[Insert | Update]: ...


class BaseRepository(abc.ABC):
    def __init__(self, session: AsyncSession, field_chains: set[str] = None, sa_loading: str = DEFAULT_SA_LOADING):
        """

        :param session:
        :param field_chains: chains to inject relationship objects (for ex.: on User ("posts", ) will give
            user with posts with user (user.posts will give an array of posts),
            but if set to None -> user.posts will be empty because weren't retrieved from db)
            doesn't work with circular referencing, for ex.: "posts.user" (from UsersRepository),
             it will throw RecursionError :p
            also affects insert and update: recursively updates/inserts objects
        :param sa_loading:
        """
        self._session = session
        self._field_chains = field_chains
        self._sa_loading = sa_loading

    @property
    def __relationship_fields__(self) -> set:
        return self.__model__.__relationship_fields__

    @property
    def __model__(self):
        """
        it gets the pydantic model class from generic base (ModelType specified in generic)
        for ex.: in `class ItemsRepository(BaseRepository, Generic[Item, ItemCreate])`
            __model__ will be returning Item
        """
        return typing.get_args(self.__class__.__orig_bases__[0])[0]  # type: ignore

    @property
    def __create_model__(self):
        """
        it gets the pydantic model class from generic base (ModelType specified in generic)
        for ex.: in `class ItemsRepository(BaseRepository, Generic[Item, ItemCreate])`
            __model__ will be returning Item
        """
        return typing.get_args(self.__class__.__orig_bases__[0])[1]  # type: ignore

    @property
    def __sa_model__(self):
        return self.__model__.__sa_model__

    @asynccontextmanager
    async def session(self) -> typing.AsyncGenerator[AsyncSession, None]:
        async with self._session.begin():
            yield self._session

    async def get(self, **kwargs):
        query = self._query(select(self.__sa_model__).filter_by(**kwargs))
        async with self.session() as s:
            result = (await s.scalars(query)).first()
            return self.__model__.from_orm(result) if result is not None else result

    async def get_or_create(self, **kwargs):
        model = await self.get(**kwargs)
        if model is None:
            model = await self.create(self.__create_model__(**kwargs))
        return model

    async def update(self, entity):
        query = update(self.__sa_model__)
        query = query.filter_by(id=entity.id)
        query = query.values(**entity.dict(exclude={"id"}.union(self.__relationship_fields__), show_secrets=True))
        query = self._query(query)

        secondary_queries = self.resolve_relationships(entity)

        async with self.session() as s:
            await s.execute(query)
            for s_query in secondary_queries:
                await s.execute(s_query)
        result = await self.get(id=entity.id)
        return result

    async def delete(self, entity):
        return await self.delete_by_id(entity.id)

    async def delete_by_id(self, id: int):
        query = delete(self.__sa_model__)
        query = query.filter_by(id=id)
        query = self._query(query)
        async with self.session() as s:
            await s.execute(query)

    async def create(self, entity):
        query = insert(self.__sa_model__).values(**entity.dict(exclude=self.__relationship_fields__, show_secrets=True))

        secondary_queries = self.resolve_relationships(entity)

        async with self.session() as s:
            result = await s.execute(query)
            id_ = result.lastrowid

            for s_query in secondary_queries:
                await s.execute(s_query)

        return await self.get(id=id_)

    async def get_many(self, **kwargs):
        query = self._query(select(self.__sa_model__).filter_by(**kwargs))
        async with self.session() as s:
            result = (await s.scalars(query))
            return [self.__model__.from_orm(result) for result in result]

    async def count(self, **kwargs):
        query = self._query(select([func.count()]).select_from(self.__sa_model__).filter_by(**kwargs))
        async with self.session() as s:
            return await s.scalar(query)

    def _query(self, query: QueryType) -> QueryType:
        """
        :param query: should be one of: Select, Delete, Insert, Update
        :return:
        """
        if self._field_chains:
            return add_loading_to_query(query, *self._field_chains, sa_loading=self._sa_loading)
        return query

    @abc.abstractmethod
    def resolve_relationships(self, entity) -> list[Insert | Update]:
        raise NotImplementedError
