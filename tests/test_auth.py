import pytest
from fastapi.testclient import TestClient


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------
def test_register_user(client: TestClient):
    payload = {
        "first_name": "Auth",
        "last_name": "User",
        "email": "authuser@test.com",
        "password": "password123",
        "organization_name": "Auth Test Org",
        "contact_phone": "9999999999"  # ✅ REQUIRED
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == payload["email"]
    assert data["organization_name"] == "Auth Test Org"
    assert data["is_org_admin"] is True


# --------------------------------------------------
# LOGIN USER
# --------------------------------------------------
def test_login_user(client: TestClient):
    payload = {
        "username": "authuser@test.com",
        "password": "password123"
    }

    response = client.post("/auth/login", data=payload)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "authuser@test.com"


# --------------------------------------------------
# AUTH STATUS (/auth/me)
# --------------------------------------------------
def test_auth_me(client: TestClient):
    response = client.get("/auth/me")

    assert response.status_code == 200
    data = response.json()

    assert data["authenticated"] is True
    assert "menus" in data
    assert "permissions" in data


# --------------------------------------------------
# REFRESH TOKEN
# --------------------------------------------------
def test_refresh_token(client: TestClient):
    response = client.post("/auth/refresh")

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
def test_logout(client: TestClient):
    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert "logged out successfully" in response.json()["message"]
