import pytest
import time
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.account_rate_limiter import _attempts

BASE_URL = "http://test"
transport = ASGITransport(app=app)


@pytest.fixture(autouse=True)
def clear_rate_limit_state():
    """Reset the in-memory rate limiter before each test so tests don't
    interfere with each other."""
    _attempts.clear()
    yield
    _attempts.clear()


@pytest.mark.asyncio
async def test_normal_user_not_blocked(test_user):
    """A single legitimate login attempt should never trip the limiter."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!",
        })
        assert resp.status_code != 429


@pytest.mark.asyncio
async def test_rapid_repeated_login_attempts_blocked(test_user):
    """6 rapid wrong-password attempts on the same account should trip
    the 5/minute limit on the 6th try."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        responses = []
        for _ in range(6):
            resp = await ac.post("/auth/login", json={
                "email": test_user.email,
                "password": "WrongPassword!",
            })
            responses.append(resp.status_code)

        assert responses[:5].count(429) == 0, "First 5 attempts should not be rate-limited"
        assert responses[5] == 429, "6th attempt should be rate-limited"


@pytest.mark.asyncio
async def test_different_accounts_not_cross_blocked(test_user):
    """Hammering one account should NOT affect a different account's ability to log in."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        # Exhaust the limit for test_user
        for _ in range(5):
            await ac.post("/auth/login", json={
                "email": test_user.email,
                "password": "WrongPassword!",
            })

        # A completely different account should be unaffected
        resp = await ac.post("/auth/login", json={
            "email": "someone_else@example.com",
            "password": "WhateverPassword!",
        })
        assert resp.status_code != 429