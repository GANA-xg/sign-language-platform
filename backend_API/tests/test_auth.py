import uuid


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_register_success(test_client):
    email = unique_email()
    response = test_client.post("/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": "TestPass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["roles"] == ["learner"]
    assert "user_id" in data


def test_register_duplicate_email_fails(test_client):
    email = unique_email()
    payload = {"full_name": "Dup User", "email": email, "password": "TestPass123"}

    first = test_client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = test_client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_login_success(test_client):
    email = unique_email()
    password = "TestPass123"
    test_client.post("/auth/register", json={
        "full_name": "Login User", "email": email, "password": password
    })

    response = test_client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == email


def test_login_wrong_password_fails(test_client):
    email = unique_email()
    test_client.post("/auth/register", json={
        "full_name": "WrongPass User", "email": email, "password": "CorrectPass123"
    })

    response = test_client.post("/auth/login", json={"email": email, "password": "WrongPass"})
    assert response.status_code == 401


def test_login_nonexistent_user_fails(test_client):
    response = test_client.post("/auth/login", json={
        "email": "doesnotexist@example.com", "password": "whatever"
    })
    assert response.status_code == 401


def test_profile_requires_auth(test_client):
    response = test_client.get("/auth/profile")
    assert response.status_code in (401, 403)  # 403 if no Authorization header at all with HTTPBearer


def test_profile_with_valid_token(test_client):
    email = unique_email()
    password = "TestPass123"
    test_client.post("/auth/register", json={
        "full_name": "Profile User", "email": email, "password": password
    })
    login_resp = test_client.post("/auth/login", json={"email": email, "password": password})
    token = login_resp.json()["access_token"]

    response = test_client.get("/auth/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_profile_with_invalid_token(test_client):
    response = test_client.get("/auth/profile", headers={"Authorization": "Bearer invalid.token.here"})
    assert response.status_code == 401