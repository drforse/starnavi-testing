import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_sign_up(fastapi_app):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/sign_up", data={"username": "test_user", "password": "test_pwd"})
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"username", "last_request_at", "id"}
        assert data["username"] == "test_user"
        assert isinstance(data["last_request_at"], int)
        assert isinstance(data["id"], int)


@pytest.mark.anyio
async def test_sign_up_exists(fastapi_app):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/sign_up", data={"username": "test_user", "password": "test_pwd"})
        assert response.status_code == 400
        assert response.json()["detail"] == "user with this username already exists"


@pytest.mark.anyio
async def test_login(fastapi_app):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/token", data={"username": "test_user", "password": "test_pwd"})
        assert response.status_code == 200
        dt = response.json()
        assert set(dt.keys()) == {"access_token", "token_type"}
        assert isinstance(dt["access_token"], str)
        assert dt["token_type"] == "bearer"


@pytest.mark.anyio
async def test_invalid_login(fastapi_app):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/token", data={"username": "test_user", "password": "invalid"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"
