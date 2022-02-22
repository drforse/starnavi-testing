from datetime import datetime, date, timedelta

import pytest

from db import UsersRepository, UserCreate, LikesRepository


@pytest.mark.anyio
async def test_get(db_session):
    repo = UsersRepository(db_session)
    user = await repo.get(id=1)
    assert user.dict(exclude={"password"}) == {
        "id": 1,
        "username": "static",
        "last_request_at": datetime.fromtimestamp(1645462963),
        "last_login_at": datetime.fromtimestamp(1645462873),
        "posts": []
    }


@pytest.mark.anyio
async def test_create(db_session):
    repo = UsersRepository(db_session)
    user_create = UserCreate(
        username="test_create",
        password="test_create_pwd"
    )
    await repo.create(user_create)
    user_in_db = await repo.get(username="test_create")
    assert user_in_db is not None


@pytest.mark.anyio
async def test_delete(db_session):
    repo = UsersRepository(db_session)
    user_in_db_old = await repo.get(username="test_create")
    await repo.delete(user_in_db_old)
    user_in_db = await repo.get(username="test_create")
    assert user_in_db_old is not None
    assert user_in_db is None


@pytest.mark.anyio
async def test_get_or_create_get(db_session):
    repo = UsersRepository(db_session)

    user_in_db = await repo.get(username="static")
    user_in_db_dup = await repo.get_or_create(username="static")
    assert user_in_db is not None
    assert user_in_db_dup is not None
    assert user_in_db == user_in_db_dup


@pytest.mark.anyio
async def test_get_or_create_create(db_session):
    repo = UsersRepository(db_session)

    user_in_db_old = await repo.get(username="test_create")
    user_in_db = await repo.get_or_create(username="test_create", password="test_create_pwd")

    assert user_in_db_old is None
    assert user_in_db is not None
    assert user_in_db.username == "test_create"

    await repo.delete(user_in_db)


@pytest.mark.anyio
async def test_delete_by_id(db_session):
    repo = UsersRepository(db_session)
    user_create = UserCreate(
        username="test_create",
        password="test_create_pwd"
    )
    await repo.create(user_create)
    user_in_db_old = await repo.get(username="test_create")

    await repo.delete_by_id(user_in_db_old.id)

    user_in_db = await repo.get(username="test_create")
    assert user_in_db is None


@pytest.mark.anyio
async def test_update(db_session):
    repo = UsersRepository(db_session)

    user_create = UserCreate(
        username="test_create",
        password="test_create_pwd"
    )
    await repo.create(user_create)
    user_in_db_old = await repo.get(username="test_create")
    last_request_at_old = user_in_db_old.last_request_at
    now = datetime(2022, 2, 22, 2, 1, 1)
    user_in_db_old.last_request_at = now
    await repo.update(user_in_db_old)
    user_in_db = await repo.get(username="test_create")

    assert user_in_db.last_request_at != last_request_at_old
    assert user_in_db.last_request_at == now

    await repo.delete(user_in_db)


@pytest.mark.anyio
async def test_get_many(db_session):
    repo = UsersRepository(db_session)
    users = await repo.get_many()
    assert len(users) == 3


@pytest.mark.anyio
async def test_count(db_session):
    repo = UsersRepository(db_session)
    count = await repo.count()
    assert count == 3


@pytest.mark.anyio
async def test_count_aggregated_by_date(db_session):
    repo = LikesRepository(db_session)
    count4 = await repo.count_aggregated_by_date(date_from=datetime(2022, 2, 21))
    count0 = await repo.count_aggregated_by_date(date_from=datetime(2022, 2, 23))
    assert count4 == 4
    assert count0 == 0
