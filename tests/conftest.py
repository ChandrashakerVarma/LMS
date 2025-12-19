<<<<<<< Updated upstream
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys

from app.main import app
from app.dependencies import get_current_user


# -----------------------------------------------------------------
# OPTIONAL: Mock ONLY OAuth2PasswordBearer, NOT entire fastapi.security
# -----------------------------------------------------------------
sys.modules["fastapi.security.oauth2"] = MagicMock()


# ------------------ CLIENT FIXTURE -----------------------
@pytest.fixture
def client():
    return TestClient(app)


# ------------------ MOCK USER FIXTURE --------------------
class DummyUser:
    id = 1
    first_name = "Sri"
    last_name = "Laxmi"
    username = "Sri Laxmi"
    email = "sri@example.com"
    is_active = True
    role = "admin"


@pytest.fixture
def mock_user():
    dummy = DummyUser()

    # This replaces Depends(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: dummy

    yield dummy

    # Cleanup after test
    app.dependency_overrides.clear()
=======
# conftest.py
from dotenv import load_dotenv
load_dotenv(".env.test", override=True)

import sys, os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import pytest
from fastapi.testclient import TestClient
from datetime import time

from app.main import app 
from app.database import get_db
from app.dependencies import get_current_user, oauth2_schema

from app.models import User, Role, Organization, Shift
from tests.test_database import create_test_db, TestingSessionLocal

# --------------------------------------------------
# DB OVERRIDE
# --------------------------------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --------------------------------------------------
# AUTH OVERRIDE
# --------------------------------------------------
def override_get_current_user():
    class FakeRole:
        name = "super_admin"

    class FakeOrg:
        id = 1
        is_active = True

    class FakeUser:
        id = 1
        first_name = "TestUser"
        role_id = 1
        role = FakeRole()
        organization_id = 1
        organization = FakeOrg()

    return FakeUser()

app.dependency_overrides[get_current_user] = override_get_current_user

# --------------------------------------------------
# DISABLE OAUTH
# --------------------------------------------------
app.dependency_overrides[oauth2_schema] = lambda: "test-token"

# --------------------------------------------------
# REMOVE PERMISSION DEPENDENCIES
# --------------------------------------------------
def strip_permissions():
    for route in app.routes:
        if hasattr(route, "dependant"):
            route.dependant.dependencies = [
                d for d in route.dependant.dependencies
                if not d.call.__module__.startswith("app.permission_dependencies")
            ]

strip_permissions()

# --------------------------------------------------
# MASTER DATA SEED
# --------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    create_test_db()
    db = TestingSessionLocal()

    org = Organization(id=1, organization_name="Test Org", is_active=True)
    role = Role(id=1, name="super_admin")

    user = User(
        id=1,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        hashed_password="dummy",
        role_id=1,
        organization_id=1,
        biometric_id="BIO12"
    )

    shift = Shift(
        id=1,
        created_by=1,
        shift_name="General Shift",
        shift_code="GEN",
        shift_type="regular",
        start_time=time(9, 0),
        end_time=time(17, 0),
        working_minutes=480,
        lag_minutes=60,
        status="active",
        is_week_off=0
    )

    db.add_all([org, role, user, shift])
    db.commit()
    db.close()
    yield

# --------------------------------------------------
# CLIENT
# --------------------------------------------------
@pytest.fixture
def client():
    return TestClient(app)
>>>>>>> Stashed changes
