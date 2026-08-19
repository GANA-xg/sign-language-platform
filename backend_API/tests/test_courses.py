import uuid
from app.database.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def make_admin(email: str):
    """Directly promote a user to admin in the DB for test purposes."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        admin_role = db.query(Role).filter(Role.role_name == "admin").first()
        db.add(UserRole(user_id=user.user_id, role_id=admin_role.role_id))
        db.commit()
    finally:
        db.close()


def register_and_login(test_client, email, password="TestPass123"):
    test_client.post("/auth/register", json={
        "full_name": "Course Test User", "email": email, "password": password
    })
    login_resp = test_client.post("/auth/login", json={"email": email, "password": password})
    return login_resp.json()["access_token"]


def test_list_lessons_public(test_client):
    response = test_client.get("/courses/lessons")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_nonexistent_lesson_returns_404(test_client):
    response = test_client.get("/courses/lessons/999999")
    assert response.status_code == 404


def test_create_lesson_blocked_for_learner(test_client):
    email = unique_email()
    token = register_and_login(test_client, email)

    response = test_client.post(
        "/courses/lessons",
        json={
            "module_id": 1,
            "title": "Test Lesson Learner",
            "sequence_order": 999,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_create_lesson_allowed_for_admin(test_client):
    email = unique_email()
    token = register_and_login(test_client, email)
    make_admin(email)

    # Need fresh token after role change
    login_resp = test_client.post("/auth/login", json={"email": email, "password": "TestPass123"})
    admin_token = login_resp.json()["access_token"]

    response = test_client.post(
        "/courses/lessons",
        json={
            "module_id": 1,
            "title": "Test Lesson Admin",
            "sequence_order": 998,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Lesson Admin"


    # cleanup
    lesson_id = data["lesson_id"]
    test_client.delete(f"/courses/lessons/{lesson_id}", headers={"Authorization": f"Bearer {admin_token}"})


def test_create_lesson_without_auth_fails(test_client):
    response = test_client.post("/courses/lessons", json={
        "module_id": 1, "title": "No Auth Lesson", "sequence_order": 997
    })
    assert response.status_code in (401, 403)