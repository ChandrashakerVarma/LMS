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
