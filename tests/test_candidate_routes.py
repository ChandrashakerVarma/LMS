import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.main import app
from app.database import get_db
from app.models.candidate_m import Candidate
from app.models.job_posting_m import JobPosting
from app.models.job_description_m import JobDescription
from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_create_permission,
    require_view_permission,
    require_edit_permission,
)

client = TestClient(app)

# --------------------------
# Fixture: DB session
# --------------------------
@pytest.fixture
def db_session():
    db = next(get_db())
    yield db
    db.rollback()

# --------------------------
# Fixture: create job description
# --------------------------
@pytest.fixture
def create_job_description(db_session: Session):
    job_desc = JobDescription(title="Test Job")
    db_session.add(job_desc)
    db_session.commit()
    db_session.refresh(job_desc)
    return job_desc

# --------------------------
# Fixture: create job posting
# --------------------------
@pytest.fixture
def create_job_posting(db_session: Session, create_job_description):
    job = JobPosting(
        job_description_id=create_job_description.id,
        number_of_positions=1,
        employment_type="Full-Time",
        location="Remote",
        created_by="TestUser",
        approval_status="accepted",
        created_at=datetime.utcnow(),
        posting_date=datetime.utcnow().date(),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job

# --------------------------
# Fixture: mock current_user and permissions
# --------------------------
@pytest.fixture(autouse=True)
def mock_dependencies():
    class DummyRole:
        name = "Admin"

    class DummyUser:
        first_name = "TestUser"
        role = DummyRole()

    app.dependency_overrides = {
        get_current_user: lambda: DummyUser(),
        require_create_permission: lambda menu_id: lambda: True,
        require_view_permission: lambda menu_id: lambda: True,
        require_edit_permission: lambda menu_id: lambda: True,
    }
    yield
    app.dependency_overrides = {}

# --------------------------
# Test: Apply candidate
# --------------------------
def test_apply_candidate(db_session, create_job_posting):
    payload = {
        "job_posting_id": str(create_job_posting.id),
        "first_name": "Ravi",
        "last_name": "Kumar",
        "email": "ravi@example.com",
        "phone": "9876543210",  # sent as Form field
    }

    # Use 'data' instead of 'json' for Form
    response = client.post("/candidates/", data=payload)
    assert response.status_code in [200, 201], response.text

    data = response.json()
    assert data["email"] == "ravi@example.com"
    assert data["job_posting_id"] == create_job_posting.id
    assert data["status"] == "Pending"

# --------------------------
# Test: Update candidate status
# --------------------------
from unittest.mock import patch
def test_update_candidate_status(db_session, create_job_posting):
    candidate = Candidate(
        job_posting_id=create_job_posting.id,
        first_name="Ravi",
        last_name="Kumar",
        email="ravi@example.com",
        phone_number="9876543210",
        applied_date=date.today(),
        status="Pending"
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)

    # Patch where the function is actually used
    with patch("app.routes.candidate_routes.send_email_ses") as mock_send_email:
        response = client.put(
            f"/candidates/{candidate.id}/status/Accepted?menu_id=1"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "Accepted"

        response = client.put(
            f"/candidates/{candidate.id}/status/Rejected?menu_id=1"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "Rejected"

        assert mock_send_email.called
