import json
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db import sa_models
from utils import config
from web.auth import get_password_hash


@pytest.fixture(scope="package", autouse=True)
async def db_session():
    engine = create_async_engine(config.TEST_SA_URL)
    DBSession: sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(sa_models.Base.metadata.create_all)
    with open("tests/data/users.json") as f:
        users = json.load(f)
    with open("tests/data/posts.json") as f:
        posts = json.load(f)
    with open("tests/data/likes.json") as f:
        likes = json.load(f)
    async with DBSession() as s:
        for user in users:
            user["last_request_at"] = datetime.fromtimestamp(user["last_request_at"])
            user["last_login_at"] = datetime.fromtimestamp(user["last_login_at"])
            user["password"] = get_password_hash(user["password"])
            m = sa_models.UserModel(**user)
            s.add(m)
        for post in posts:
            post["created_at"] = datetime.fromtimestamp(post["created_at"])
            s.add(sa_models.PostModel(**post))
        for like in likes:
            like["created_at"] = datetime.fromtimestamp(like["created_at"])
            s.add(sa_models.LikeModel(**like))
        await s.commit()
    async with DBSession() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(sa_models.Base.metadata.drop_all)
    await engine.dispose()