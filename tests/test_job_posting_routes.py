import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user
from datetime import date
import random

# ------------------ DUMMY USER + ROLE -----------------------
class DummyRole:
    name = "admin"

class DummyUser:
    id = 1
    first_name = "Sri"
    last_name = "Laxmi"
    username = "Sri Laxmi"
    email = "sri@example.com"
    is_active = True
    role = DummyRole()

# ------------------ OVERRIDE DEPENDENCY -----------------------
@pytest.fixture(scope="module", autouse=True)
def override_user_dependency():
    def fake_user():
        return DummyUser()
    app.dependency_overrides[get_current_user] = fake_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

# ------------------ CLIENT FIXTURE ---------------------------
@pytest.fixture
def client():
    return TestClient(app)

# ------------------ TEST CASES -----------------------------
def test_create_job_posting(client):
    job_description_id = 1  # Make sure this exists in your DB
    unique_location = f"Hyderabad-{random.randint(1, 10000)}"
    payload = {
        "job_description_id": job_description_id,
        "number_of_positions": 2,
        "employment_type": "Full-time",
        "location": unique_location,
        "salary": 1000000,
        "posting_date": str(date.today()),
        "closing_date": str(date.today())
    }
    response = client.post("/job-postings/", json=payload)
    assert response.status_code in [200, 201], f"Response: {response.json()}"
    data = response.json()
    assert "id" in data
    assert data["location"] == unique_location

def test_get_all_job_postings(client):
    response = client.get("/job-postings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_job_posting_by_id(client):
    response = client.get("/job-postings/1")
    assert response.status_code in [200, 404]

def test_filter_job_postings(client):
    response = client.get("/job-postings/filters?location=Hyderabad")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_dashboard(client):
    response = client.get("/job-postings/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
