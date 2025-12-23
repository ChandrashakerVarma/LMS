import pytest

# ====================================
# CREATE
# ====================================
def test_create_job_description_success(client):
    response = client.post("/job-descriptions/", json={
        "title": "Senior Software Engineer",
        "description": "Backend APIs",
        "requirements": "Python",
        "responsibilities": "Develop APIs",
        "department": "Engineering"
    })
    assert response.status_code == 200  # API returns 200
    assert "id" in response.json()


def test_create_job_description_missing_fields(client):
    response = client.post("/job-descriptions/", json={
        "title": "Only Title"
    })
    assert response.status_code == 200  # API allows it


# ====================================
# READ
# ====================================
def test_get_all_job_descriptions(client):
    response = client.get("/job-descriptions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_job_description(client):
    create = client.post("/job-descriptions/", json={
        "title": "DevOps",
        "description": "Infra",
        "requirements": "AWS",
        "responsibilities": "Deploy",
        "department": "Ops"
    })
    job_id = create.json()["id"]

    response = client.get(f"/job-descriptions/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_get_single_job_description_not_found(client):
    response = client.get("/job-descriptions/999999")
    assert response.status_code == 404


# ====================================
# UPDATE
# ====================================
def test_update_job_description(client):
    create = client.post("/job-descriptions/", json={
        "title": "QA",
        "description": "Testing",
        "requirements": "Manual",
        "responsibilities": "Test",
        "department": "QA"
    })
    job_id = create.json()["id"]

    response = client.put(f"/job-descriptions/{job_id}", json={
        "title": "Senior QA",
        "description": "Automation",
        "requirements": "Pytest",
        "responsibilities": "Automate",
        "department": "QA"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Senior QA"


# ====================================
# DELETE
# ====================================
def test_delete_job_description(client):
    create = client.post("/job-descriptions/", json={
        "title": "HR",
        "description": "People",
        "requirements": "HR Skills",
        "responsibilities": "Hire",
        "department": "HR"
    })
    job_id = create.json()["id"]

    response = client.delete(f"/job-descriptions/{job_id}")
    assert response.status_code == 200

    response = client.get(f"/job-descriptions/{job_id}")
    assert response.status_code == 404
