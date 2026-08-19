import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE_URL = "http://test"
transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_rejects_script_tag_in_title(test_user):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/notifications/", json={
            "user_id": str(test_user.user_id),
            "notification_type": "badge_earned",
            "title": "<script>alert('xss')</script>",
            "message": "Test message",
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_rejects_sql_injection_in_message(test_user):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/notifications/", json={
            "user_id": str(test_user.user_id),
            "notification_type": "badge_earned",
            "title": "Valid Title",
            "message": "'; DROP TABLE users; --",
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_rejects_oversized_message(test_user):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/notifications/", json={
            "user_id": str(test_user.user_id),
            "notification_type": "badge_earned",
            "title": "Valid Title",
            "message": "A" * 2000,
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_rejects_invalid_notification_type(test_user):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/notifications/", json={
            "user_id": str(test_user.user_id),
            "notification_type": "not_a_real_type",
            "title": "Valid Title",
            "message": "Valid message",
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_accepts_valid_notification(test_user):
    """Sanity check — valid input should still work normally."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/notifications/", json={
            "user_id": str(test_user.user_id),
            "notification_type": "badge_earned",
            "title": "You earned a badge!",
            "message": "Great job completing all letters.",
        })
        assert resp.status_code == 201