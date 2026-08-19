"""
Milestone 3 - Day 8
Full-journey integration tests: chains multiple endpoints together to
simulate a real user's path, rather than testing endpoints in isolation
(Day 7's job).
"""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

BASE_URL = "http://test"
transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_journey_register_login_view_lessons():
    """Journey 1: register -> login -> view own profile -> browse lessons."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"journey1_{uuid.uuid4().hex[:8]}@example.com"

        register_resp = await ac.post("/auth/register", json={
            "email": email, "password": "JourneyPass123!", "full_name": "Journey One",
        })
        assert register_resp.status_code == 201
        assert "learner" in register_resp.json()["roles"]

        login_resp = await ac.post("/auth/login", json={
            "email": email, "password": "JourneyPass123!",
        })
        assert login_resp.status_code == 200
        access_token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        profile_resp = await ac.get("/auth/profile", headers=headers)
        assert profile_resp.status_code == 200
        assert profile_resp.json()["email"] == email

        lessons_resp = await ac.get("/courses/lessons")
        assert lessons_resp.status_code == 200
        assert isinstance(lessons_resp.json(), list)


@pytest.mark.asyncio
async def test_journey_earn_badge_get_notified_read_it():
    """Journey 2: register -> login -> badge notification created -> appears in list -> marked read."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"journey2_{uuid.uuid4().hex[:8]}@example.com"

        register_resp = await ac.post("/auth/register", json={
            "email": email, "password": "JourneyPass123!", "full_name": "Journey Two",
        })
        user_id = register_resp.json()["user_id"]

        login_resp = await ac.post("/auth/login", json={
            "email": email, "password": "JourneyPass123!",
        })
        access_token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        create_notif_resp = await ac.post("/notifications/", json={
            "user_id": user_id,
            "notification_type": "badge_earned",
            "title": "Alphabet Master!",
            "message": "You completed all letters with 80%+ accuracy.",
        })
        assert create_notif_resp.status_code == 201
        notification_id = create_notif_resp.json()["notification_id"]

        list_resp = await ac.get("/notifications/me", headers=headers)
        assert list_resp.status_code == 200
        notif_ids = [n["notification_id"] for n in list_resp.json()]
        assert notification_id in notif_ids

        mark_read_resp = await ac.patch(f"/notifications/{notification_id}/read", headers=headers)
        assert mark_read_resp.status_code == 200
        assert mark_read_resp.json()["is_read"] is True


@pytest.mark.asyncio
async def test_journey_password_change_then_relogin():
    """Journey 3: register -> login -> change password -> old password fails -> new password works."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"journey3_{uuid.uuid4().hex[:8]}@example.com"
        old_password = "OldPass123!"
        new_password = "NewPass456!"

        await ac.post("/auth/register", json={
            "email": email, "password": old_password, "full_name": "Journey Three",
        })

        login_resp = await ac.post("/auth/login", json={
            "email": email, "password": old_password,
        })
        access_token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        change_resp = await ac.put("/auth/me/password", headers=headers, json={
            "old_password": old_password,
            "new_password": new_password,
        })
        assert change_resp.status_code == 200

        old_login_resp = await ac.post("/auth/login", json={
            "email": email, "password": old_password,
        })
        assert old_login_resp.status_code == 401

        new_login_resp = await ac.post("/auth/login", json={
            "email": email, "password": new_password,
        })
        assert new_login_resp.status_code == 200


@pytest.mark.asyncio
async def test_journey_admin_deactivates_user_who_then_cannot_login():
    """Journey 4: admin bulk-deactivates a learner -> that learner is blocked from logging in."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        learner_email = f"journey4_learner_{uuid.uuid4().hex[:8]}@example.com"
        password = "LearnerPass123!"
        register_resp = await ac.post("/auth/register", json={
            "email": learner_email, "password": password, "full_name": "Soon Deactivated",
        })
        learner_user_id = register_resp.json()["user_id"]

        from app.database.session import SessionLocal
        from app.models.user import User
        from app.models.role import Role
        from app.models.user_role import UserRole
        from app.core.security import hash_password

        db = SessionLocal()
        admin_email = f"journey4_admin_{uuid.uuid4().hex[:8]}@example.com"
        admin_user = User(
            email=admin_email,
            password_hash=hash_password("AdminPass123!"),
            full_name="Journey Admin",
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        admin_role = db.query(Role).filter(Role.role_name == "admin").first()
        db.add(UserRole(user_id=admin_user.user_id, role_id=admin_role.role_id))
        db.commit()
        db.close()

        admin_login_resp = await ac.post("/auth/login", json={
            "email": admin_email, "password": "AdminPass123!",
        })
        admin_token = admin_login_resp.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        bulk_resp = await ac.post("/admin/users/bulk-action", headers=admin_headers, json={
            "user_ids": [learner_user_id],
            "action": "deactivate",
        })
        assert bulk_resp.status_code == 200
        assert bulk_resp.json()["updated_count"] == 1

        learner_login_resp = await ac.post("/auth/login", json={
            "email": learner_email, "password": password,
        })
        assert learner_login_resp.status_code in (401, 403)