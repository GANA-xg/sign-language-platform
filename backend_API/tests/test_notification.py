import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.notification_service import (
    notify_badge_earned,
    notify_streak_milestone,
    notify_certificate_ready,
    notify_new_recommendation,
)

BASE_URL = "http://test"
transport = ASGITransport(app=app)


def test_notify_badge_earned(db_session, test_user):
    notification = notify_badge_earned(
        db=db_session, user_id=test_user.user_id, badge_id=1, badge_name="Alphabet Master",
    )
    assert notification.notification_type == "badge_earned"
    assert "Alphabet Master" in notification.message
    assert notification.is_read is False


def test_notify_streak_milestone(db_session, test_user):
    notification = notify_streak_milestone(db=db_session, user_id=test_user.user_id, streak_days=7)
    assert notification.notification_type == "streak_milestone"
    assert "7" in notification.message


def test_notify_certificate_ready(db_session, test_user):
    notification = notify_certificate_ready(
        db=db_session, user_id=test_user.user_id, certificate_id=uuid.uuid4(),
    )
    assert notification.notification_type == "certificate_ready"


def test_notify_new_recommendation(db_session, test_user):
    notification = notify_new_recommendation(
        db=db_session, user_id=test_user.user_id, lesson_id=1, lesson_name="Letter Z",
    )
    assert notification.notification_type == "new_recommendation"
    assert "Letter Z" in notification.message


@pytest.mark.asyncio
async def test_create_notification_api(test_user):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/notifications/", json={
            "user_id": str(test_user.user_id),
            "notification_type": "badge_earned",
            "title": "New Badge Earned!",
            "message": "You earned the Alphabet Master badge.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["notification_type"] == "badge_earned"
        assert data["is_read"] is False


@pytest.mark.asyncio
async def test_get_my_notifications(auth_headers):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/notifications/me", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_mark_notification_as_read(db_session, test_user, auth_headers):
    notification = notify_badge_earned(
        db=db_session, user_id=test_user.user_id, badge_id=1, badge_name="Test Badge",
    )
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.patch(f"/notifications/{notification.notification_id}/read", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["is_read"] is True


@pytest.mark.asyncio
async def test_mark_notification_as_read_not_found(auth_headers):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.patch("/notifications/999999999/read", headers=auth_headers)
        assert resp.status_code == 404