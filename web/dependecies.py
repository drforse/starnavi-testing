from db.core import DBSession


async def get_db_session():
    async with DBSession() as s:
        yield s
