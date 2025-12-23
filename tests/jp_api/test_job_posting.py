# tests/api/test_job_posting.py
from datetime import date


# ---------------------------------------------------
# JOB PAYLOAD
# ---------------------------------------------------
def get_job_payload(organization, branch, job_description):
    return {
        "organization_id": organization.id,
        "branch_id": branch.id,
        "job_description_id": job_description.id,
        "job_type": "fresher",
        "number_of_positions": 5,
        "employment_type": "Full Time",
        "location": "Bangalore",
        "salary": 50000,
        "posting_date": date.today().isoformat()
    }


# ---------------------------------------------------
# CREATE JOB POSTING
# ---------------------------------------------------
def test_create_job_posting_success(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)
    response = client.post("/job-postings/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["location"] == "Bangalore"


# ---------------------------------------------------
# DUPLICATE JOB POSTING
# ---------------------------------------------------
def test_create_job_posting_duplicate(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)

    client.post("/job-postings/", json=payload)
    response = client.post("/job-postings/", json=payload)

    assert response.status_code == 400


# ---------------------------------------------------
# GET ALL JOB POSTINGS
# ---------------------------------------------------
def test_get_all_job_postings(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)
    client.post("/job-postings/", json=payload)

    response = client.get("/job-postings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------
# GET SINGLE JOB POSTING
# ---------------------------------------------------
def test_get_single_job_posting(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)
    create_res = client.post("/job-postings/", json=payload)

    job_id = create_res.json()["id"]
    response = client.get(f"/job-postings/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id


# ---------------------------------------------------
# NOT FOUND
# ---------------------------------------------------
def test_get_single_job_posting_not_found(client):
    response = client.get("/job-postings/999999")
    assert response.status_code == 404


# ---------------------------------------------------
# UPDATE JOB POSTING
# ---------------------------------------------------
def test_update_job_posting_success(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)
    create_res = client.post("/job-postings/", json=payload)
    job_id = create_res.json()["id"]

    response = client.put(
        f"/job-postings/{job_id}",
        json={"location": "Hyderabad", "salary": 60000}
    )

    assert response.status_code == 200
    assert response.json()["location"] == "Hyderabad"


# ---------------------------------------------------
# DELETE JOB POSTING
# ---------------------------------------------------
def test_delete_job_posting(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)
    create_res = client.post("/job-postings/", json=payload)
    job_id = create_res.json()["id"]

    response = client.delete(f"/job-postings/{job_id}")
    assert response.status_code == 200

    get_res = client.get(f"/job-postings/{job_id}")
    assert get_res.status_code == 404


# ---------------------------------------------------
# FILTER JOB POSTINGS
# ---------------------------------------------------
def test_filter_by_location(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)
    client.post("/job-postings/", json=payload)

    response = client.get("/job-postings/filters?location=Bangalore")

    assert response.status_code == 200
    assert len(response.json()) >= 1


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
def test_dashboard(
    client, organization, branch, job_description
):
    payload = get_job_payload(organization, branch, job_description)
    client.post("/job-postings/", json=payload)

    response = client.get("/job-postings/dashboard")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    dashboard = response.json()[0]
    assert "job_id" in dashboard
    assert "total_candidates" in dashboard
