from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from utils import config
from . import sa_models

engine = create_async_engine(config.SA_URL, echo=config.SA_ECHO)
DBSession: sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def recreate_db():
    async with engine.begin() as conn:
        await conn.run_sync(sa_models.Base.metadata.drop_all)
        await conn.run_sync(sa_models.Base.metadata.create_all)

    await engine.dispose()


# import asyncio; asyncio.run(recreate_db())
