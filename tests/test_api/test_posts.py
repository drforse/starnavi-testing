import pytest
from httpx import AsyncClient

from db import LikesRepository


@pytest.fixture(scope="module")
async def token(fastapi_app):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/token", data={"username": "static", "password": "static"})
        return response.json()["access_token"]


@pytest.mark.anyio
async def test_post_create(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/posts", json={"text": "Hello World!"},
                                 headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        data = response.json()
        assert set(data.keys()) == {"id", "created_at", "user_id", "text"}
        assert data["user_id"] == 1
        assert isinstance(data["created_at"], int)
        assert data["id"] == 4
        assert data["text"] == "Hello World!"


@pytest.mark.anyio
async def test_post_create_too_long(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/posts", json={"text": "c"*66000},
                                 headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422


@pytest.mark.anyio
async def test_post_create_with_user(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/posts?fields=user", json={"text": "Hello World!"},
                                 headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        data = response.json()
        assert set(data.keys()) == {"id", "created_at", "user_id", "user", "text"}
        assert data["user_id"] == 1
        assert isinstance(data["created_at"], int)
        assert data["id"] == 5
        assert data["text"] == "Hello World!"
        assert set(data["user"].keys()) == {"id", "username", "last_request_at", "last_login_at"}
        assert data["user"]["id"] == data["user_id"]
        assert data["user"]["username"] == "static"
        assert isinstance(data["user"]["last_request_at"], int)
        assert isinstance(data["user"]["last_login_at"], int)


@pytest.mark.anyio
async def test_post_like(fastapi_app, db_session, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/posts/1/like", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
    likes = LikesRepository(db_session)
    like = await likes.get(post_id=1, user_id=1)
    assert like is not None


@pytest.mark.anyio
async def test_post_like_twice(fastapi_app, db_session, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/posts/1/like", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 400
        assert response.json()["detail"] == "already liked"


@pytest.mark.anyio
async def test_post_like_404(fastapi_app, db_session, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/posts/0/like", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
        assert response.json()["detail"] == "post not found"


@pytest.mark.anyio
async def test_post_unlike(fastapi_app, db_session, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.delete("/posts/1/like", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204


@pytest.mark.anyio
async def test_post_unlike_twice(fastapi_app, db_session, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.delete("/posts/1/like", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
        assert response.json()["detail"] == "like not found"


@pytest.mark.anyio
async def test_post_unlike_post_does_not_exist(fastapi_app, db_session, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.delete("/posts/0/like", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
        assert response.json()["detail"] == "post not found"
