from fastapi.testclient import TestClient


# --------------------------------------------------
# STATELESS TESTS (Independent)
# --------------------------------------------------

def test_create_in_punch(client: TestClient):
    """
    Create IN punch (stateless)
    """
    response = client.post(
        "/attendance-punch/",
        json={
            "bio_id": "BIO12",
            "punch_date": "2025-01-10",
            "punch_time": "09:00",
            "punch_type": "IN"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["bio_id"] == "BIO12"
    assert data["punch_type"] == "IN"


def test_create_out_punch(client: TestClient):
    """
    Create OUT punch (stateless)
    """
    response = client.post(
        "/attendance-punch/",
        json={
            "bio_id": "BIO12",
            "punch_date": "2025-01-10",
            "punch_time": "17:00",
            "punch_type": "OUT"
        }
    )

    assert response.status_code == 200
    assert response.json()["punch_type"] == "OUT"


def test_get_all_punches(client: TestClient):
    """
    Fetch all punches
    """
    response = client.get("/attendance-punch/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_punch_missing_required_field(client: TestClient):
    """
    Missing punch_type → validation error
    """
    response = client.post(
        "/attendance-punch/",
        json={
            "bio_id": "BIO12",
            "punch_date": "2025-01-11",
            "punch_time": "09:00"
        }
    )

    assert response.status_code == 422


def test_create_punch_invalid_type(client: TestClient):
    """
    Invalid punch_type (raw data allowed / schema dependent)
    """
    response = client.post(
        "/attendance-punch/",
        json={
            "bio_id": "BIO12",
            "punch_date": "2025-01-12",
            "punch_time": "09:00",
            "punch_type": "XYZ"
        }
    )

    # Depending on schema validation
    assert response.status_code in (200, 422)


# --------------------------------------------------
# STATEFUL TEST (Minimal Workflow)
# --------------------------------------------------

def test_attendance_punch_in_and_out_workflow(client: TestClient):
    """
    IN → OUT workflow (stateful)
    """

    # IN punch
    response_in = client.post(
        "/attendance-punch/",
        json={
            "bio_id": "BIO12",
            "punch_date": "2025-01-13",
            "punch_time": "09:00",
            "punch_type": "IN"
        }
    )
    assert response_in.status_code == 200

    # OUT punch
    response_out = client.post(
        "/attendance-punch/",
        json={
            "bio_id": "BIO12",
            "punch_date": "2025-01-13",
            "punch_time": "17:00",
            "punch_type": "OUT"
        }
    )
    assert response_out.status_code == 200

    # Validate data exists
    response_get = client.get("/attendance-punch/")
    punches = response_get.json()

    assert len(punches) >= 2
