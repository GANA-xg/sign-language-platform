import os
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.role import Role

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def ensure_roles_seeded():
    """Make sure default roles exist before any test runs."""
    db = SessionLocal()
    try:
        for role_name in ["learner", "instructor", "trainer", "admin"]:
            if not db.query(Role).filter(Role.role_name == role_name).first():
                db.add(Role(role_name=role_name))
        db.commit()
    finally:
        db.close()


@pytest.fixture
def test_client():
    return client


import uuid
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import hash_password, create_access_token


@pytest.fixture
def db_session():
    """Provides a DB session for direct model/service-layer tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    email = "notif_test_user@example.com"
    user = db_session.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password("TestPass123!"),
            full_name="Notif Test User",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        role = db_session.query(Role).filter(Role.role_name == "learner").first()
        link = UserRole(user_id=user.user_id, role_id=role.role_id)
        db_session.add(link)
        db_session.commit()

    # Always reset to active — a previous test run may have deactivated this
    # shared user (e.g. bulk-action test), so guarantee a clean state here.
    if not user.is_active:
        user.is_active = True
        db_session.commit()
        db_session.refresh(user)

    return user


@pytest.fixture
def auth_headers(test_user):
    """Generates a valid Bearer token header for the test user."""
    token = create_access_token({"sub": str(test_user.user_id)})
    return {"Authorization": f"Bearer {token}"}