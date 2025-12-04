import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models.job_description_m import JobDescription
from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_create_permission,
    require_view_permission,
    require_edit_permission,
    require_delete_permission,
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
# Fixture: create JobDescription
# --------------------------
@pytest.fixture
def create_job_description(db_session: Session):
    job_description = JobDescription(
        title="Sample Title",
        description="Sample Description",
        required_skills="Python, FastAPI",
        created_by="Tester",
        modified_by=None
    )
    db_session.add(job_description)
    db_session.commit()
    db_session.refresh(job_description)
    return job_description


# --------------------------
# Mock current_user and permissions
# --------------------------
@pytest.fixture(autouse=True)
def mock_dependencies():
    class DummyRole:
        name = "Admin"

    class DummyUser:
        first_name = "TestUser"
        role = DummyRole()  # role must have .name

    # Override actual dependency functions
    app.dependency_overrides = {
        get_current_user: lambda: DummyUser(),
        require_create_permission: lambda menu_id: lambda: True,
        require_view_permission: lambda menu_id: lambda: True,
        require_edit_permission: lambda menu_id: lambda: True,
        require_delete_permission: lambda menu_id: lambda: True,
    }
    yield
    app.dependency_overrides = {}


# --------------------------
# Test: Create JobDescription
# --------------------------
def test_create_job_description():
    payload = {
        "title": "New Job Title",
        "description": "New Job Description",
        "required_skills": "Python, SQLAlchemy"
    }
    response = client.post("/job-descriptions/", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["title"] == "New Job Title"
    assert data["description"] == "New Job Description"
    assert data["required_skills"] == "Python, SQLAlchemy"


# --------------------------
# Test: Get all JobDescriptions
# --------------------------
def test_get_all_descriptions(create_job_description):
    response = client.get("/job-descriptions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(d["title"] == "Sample Title" for d in data)


# --------------------------
# Test: Get single JobDescription
# --------------------------
def test_get_job_description(create_job_description):
    jd_id = create_job_description.id
    response = client.get(f"/job-descriptions/{jd_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == jd_id
    assert data["title"] == "Sample Title"


# --------------------------
# Test: Update JobDescription
# --------------------------
def test_update_job_description(create_job_description):
    jd_id = create_job_description.id
    payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "required_skills": "Updated Skill"
    }
    response = client.put(f"/job-descriptions/{jd_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["required_skills"] == "Updated Skill"


# --------------------------
# Test: Delete JobDescription
# --------------------------
def test_delete_job_description(create_job_description):
    jd_id = create_job_description.id
    response = client.delete(f"/job-descriptions/{jd_id}")
    assert response.status_code == 200
    data = response.json()
    assert "deleted by" in data["detail"]

    # Verify deletion
    response = client.get(f"/job-descriptions/{jd_id}")
    assert response.status_code == 404
