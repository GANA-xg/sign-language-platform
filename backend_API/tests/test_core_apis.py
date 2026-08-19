"""
Milestone 3 - Day 7
Automated tests for core platform APIs (10+ key endpoints).
Covers both happy paths and key failure/security cases.
"""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

BASE_URL = "http://test"
transport = ASGITransport(app=app)


# ---------------------------------------------------------------------------
# 1. Health
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 2. Auth: register
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_new_user_succeeds():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        unique_email = f"day7_{uuid.uuid4().hex[:8]}@example.com"
        resp = await ac.post("/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Day7 Test User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == unique_email
        assert "learner" in data["roles"]


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"day7_dup_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"email": email, "password": "TestPass123!", "full_name": "Dup Test"}

        first = await ac.post("/auth/register", json=payload)
        assert first.status_code == 201

        second = await ac.post("/auth/register", json=payload)
        assert second.status_code == 409  # already registered


# ---------------------------------------------------------------------------
# 3. Auth: login (happy path + wrong password)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_with_correct_credentials():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"day7_login_{uuid.uuid4().hex[:8]}@example.com"
        await ac.post("/auth/register", json={
            "email": email, "password": "TestPass123!", "full_name": "Login Test"
        })

        resp = await ac.post("/auth/login", json={"email": email, "password": "TestPass123!"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_with_wrong_password_rejected():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"day7_wrongpw_{uuid.uuid4().hex[:8]}@example.com"
        await ac.post("/auth/register", json={
            "email": email, "password": "TestPass123!", "full_name": "Wrong PW Test"
        })

        resp = await ac.post("/auth/login", json={"email": email, "password": "WrongPassword!"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 4. Auth: refresh token
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_refresh_token_rotates_successfully():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"day7_refresh_{uuid.uuid4().hex[:8]}@example.com"
        await ac.post("/auth/register", json={
            "email": email, "password": "TestPass123!", "full_name": "Refresh Test"
        })
        login_resp = await ac.post("/auth/login", json={"email": email, "password": "TestPass123!"})
        refresh_token = login_resp.json()["refresh_token"]

        resp = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

        # Old refresh token should now be revoked — reusing it should fail
        reuse_resp = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert reuse_resp.status_code == 401


# ---------------------------------------------------------------------------
# 5. Auth: profile (requires auth)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_profile_requires_authentication():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/auth/profile")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_profile_with_valid_token(auth_headers, test_user):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/auth/profile", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == test_user.email


# ---------------------------------------------------------------------------
# 6. Courses: list lessons
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_lessons_returns_list():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/courses/lessons")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# 7. Admin: list users requires admin role (learner should be forbidden)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_users_forbidden_for_learner():
    """Uses a fresh, guaranteed learner-only account, independent of
    whatever roles the shared test_user fixture currently has."""
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"day7_learner_only_{uuid.uuid4().hex[:8]}@example.com"
        await ac.post("/auth/register", json={
            "email": email, "password": "TestPass123!", "full_name": "Learner Only",
        })
        login_resp = await ac.post("/auth/login", json={"email": email, "password": "TestPass123!"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await ac.get("/admin/users", headers=headers)
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_users_unauthenticated_rejected():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.get("/admin/users")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 8. Notifications: create + list (already have dedicated file, quick smoke here)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_notification_full_flow(test_user, auth_headers):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        create_resp = await ac.post("/notifications/", json={
            "user_id": str(test_user.user_id),
            "notification_type": "badge_earned",
            "title": "Day 7 Test Badge",
            "message": "Testing full notification flow",
        })
        assert create_resp.status_code == 201
        notif_id = create_resp.json()["notification_id"]

        list_resp = await ac.get("/notifications/me", headers=auth_headers)
        assert list_resp.status_code == 200
        assert any(n["notification_id"] == notif_id for n in list_resp.json())

        read_resp = await ac.patch(f"/notifications/{notif_id}/read", headers=auth_headers)
        assert read_resp.status_code == 200
        assert read_resp.json()["is_read"] is True


# ---------------------------------------------------------------------------
# 9. Logout revokes refresh token
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_logout_revokes_refresh_token():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        email = f"day7_logout_{uuid.uuid4().hex[:8]}@example.com"
        await ac.post("/auth/register", json={
            "email": email, "password": "TestPass123!", "full_name": "Logout Test"
        })
        login_resp = await ac.post("/auth/login", json={"email": email, "password": "TestPass123!"})
        refresh_token = login_resp.json()["refresh_token"]

        logout_resp = await ac.post("/auth/logout", json={"refresh_token": refresh_token})
        assert logout_resp.status_code == 200

        # Token should now be unusable
        reuse_resp = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert reuse_resp.status_code == 401


# ---------------------------------------------------------------------------
# 10. Change password (requires auth, requires correct old password)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_change_password_with_wrong_old_password_rejected(auth_headers):
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.put("/auth/me/password", headers=auth_headers, json={
            "old_password": "DefinitelyWrongPassword!",
            "new_password": "NewPass123!",
        })
        assert resp.status_code == 401