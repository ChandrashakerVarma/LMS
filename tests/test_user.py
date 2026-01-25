import pytest
from fastapi.testclient import TestClient

from app.models.user_m import User
from app.models.role_m import Role
from app.models.shift_roster_m import ShiftRoster

# --------------------------------------------------
# CREATE USER
# --------------------------------------------------
def test_create_user(client: TestClient, db):
    role = db.query(Role).filter(Role.name == "employee").first()
    if not role:
        role = Role(name="employee")
        db.add(role)
        db.commit()
        db.refresh(role)

    payload = {
        "first_name": "Test",
        "last_name": "Employee",
        "email": "employee1@test.com",
        "password": "password123",
        "role_id": role.id,
        "designation": "Software Engineer",
        "inactive": False,
        "biometric_id": "BIO_EMP_01",
        "branch_id": None
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]

# --------------------------------------------------
# GET USERS
# --------------------------------------------------
def test_get_users(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 200

# --------------------------------------------------
# GET USER BY ID
# --------------------------------------------------
def test_get_user_by_id(client: TestClient, db):
    user = db.query(User).filter(User.email == "employee1@test.com").first()
    assert user is not None

    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200

# --------------------------------------------------
# UPDATE USER
# --------------------------------------------------
def test_update_user(client: TestClient, db):
    user = db.query(User).filter(User.email == "employee1@test.com").first()
    assert user is not None

    response = client.put(
        f"/users/{user.id}",
        json={"designation": "Senior Software Engineer"}
    )

    assert response.status_code == 200
    assert response.json()["designation"] == "Senior Software Engineer"

# --------------------------------------------------
# ASSIGN SHIFT ROSTER
# --------------------------------------------------
def test_assign_shift_roster_to_user(client: TestClient, db):
    user = db.query(User).filter(User.email == "employee1@test.com").first()
    assert user is not None

    roster = ShiftRoster(name="Default Roster", created_by="test")
    db.add(roster)
    db.commit()
    db.refresh(roster)

    response = client.patch(f"/users/update-shift/{user.id}/{roster.id}")
    assert response.status_code == 200

# --------------------------------------------------
# MAKE ORG ADMIN
# --------------------------------------------------
def test_make_user_org_admin(client: TestClient, db):
    user = db.query(User).filter(User.email == "employee1@test.com").first()
    assert user is not None

    response = client.patch(f"/users/{user.id}/make-org-admin")
    assert response.status_code == 200

# --------------------------------------------------
# DELETE USER
# --------------------------------------------------
def test_delete_user(client: TestClient, db):
    user = db.query(User).filter(User.email == "employee1@test.com").first()
    assert user is not None

    response = client.delete(f"/users/{user.id}")
    assert response.status_code == 204
