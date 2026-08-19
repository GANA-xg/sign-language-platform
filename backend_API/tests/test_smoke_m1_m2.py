# tests/test_smoke_m1_m2.py
"""
Day 1 - Milestone 3
Re-tests core Milestone 1 & 2 endpoints to confirm nothing broke
before starting new Milestone 3 work.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app  # adjust import to your actual app entrypoint

BASE_URL = "http://test"
transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_user_register_login_flow():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        register_resp = await ac.post("/auth/register", json={
            "email": "smoketest12@example.com",
            "password": "TestPass12345!",
            "full_name": "Smoke Test12"
        })
        assert register_resp.status_code in (200, 201, 400,409)

        login_resp = await ac.post("/auth/login", json={
            "email": "smoketest12@example.com",
            "password": "TestPass12345!"
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()


@pytest.mark.asyncio
async def test_refresh_token_rotation():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        login_resp = await ac.post("/auth/login", json={
            "email": "smoketest@example.com",
            "password": "TestPass123!"
        })
        refresh_token = login_resp.json().get("refresh_token")
        assert refresh_token is not None

        refresh_resp = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 200
        assert "access_token" in refresh_resp.json()


@pytest.mark.asyncio
async def test_get_courses_list():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/courses/lessons")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_admin_endpoints_still_gated():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/admin/users")
        assert resp.status_code in (401, 403)