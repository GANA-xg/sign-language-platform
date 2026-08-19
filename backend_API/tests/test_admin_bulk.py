import io
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE_URL = "http://test"
transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_bulk_user_action(auth_headers, db_session):
    from app.models.user import User
    from app.core.security import hash_password
    import uuid

    # Create a disposable user just for this test — never touch the shared test_user
    throwaway = User(
        email=f"bulk_test_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("TempPass123!"),
        full_name="Bulk Action Target",
    )
    db_session.add(throwaway)
    db_session.commit()
    db_session.refresh(throwaway)

    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/admin/users/bulk-action", headers=auth_headers, json={
            "user_ids": [str(throwaway.user_id)],
            "action": "deactivate",
        })
        assert resp.status_code in (200, 403)


@pytest.mark.asyncio
async def test_bulk_lesson_upload(auth_headers):
    csv_content = (
        "module_id,title,sequence_order,difficulty_level,category\n"
        "1,Test Lesson A,5,beginner,Alphabet\n"
        "1,Test Lesson B,6,intermediate,Alphabet\n"
    )
    files = {"file": ("lessons.csv", io.BytesIO(csv_content.encode()), "text/csv")}

    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        resp = await ac.post("/admin/lessons/bulk-upload", headers=auth_headers, files=files)
        assert resp.status_code in (200, 403)