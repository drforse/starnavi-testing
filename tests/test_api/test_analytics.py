import pytest
from httpx import AsyncClient


@pytest.fixture(scope="module")
async def token(fastapi_app):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.post("/token", data={"username": "static2", "password": "static2"})
        return response.json()["access_token"]


@pytest.mark.anyio
async def test_analytics(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/analytics", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == {"all_likes_count": 4, "user_likes_count": 2}


@pytest.mark.anyio
async def test_analytics_with_dates_range(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/analytics?date_from=2022-02-21&date_to=2022-02-23", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == {"all_likes_count": 4, "user_likes_count": 2}


@pytest.mark.anyio
async def test_analytics_with_dates_range_1(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/analytics?date_to=2022-02-21", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == {"all_likes_count": 0, "user_likes_count": 0}


@pytest.mark.anyio
async def test_user_profile(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/user/2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == {
            "id": 2,
            "username": "static1",
            "last_request_at": 1645462432,
            "last_login_at": 1645462231
        }


@pytest.mark.anyio
async def test_user_profile_404(fastapi_app, token):
    async with AsyncClient(app=fastapi_app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/user/5", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
