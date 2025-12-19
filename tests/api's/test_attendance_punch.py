from fastapi.testclient import TestClient

def create_sample_punch(client: TestClient):
    client.post("/attendance-punch/", json={
        "bio_id": "BIO12",
        "punch_date": "2025-12-17",
        "punch_time": "09:00:00",
        "punch_type": "IN"
    })

    client.post("/attendance-punch/", json={
        "bio_id": "BIO12",
        "punch_date": "2025-12-17",
        "punch_time": "17:00:00",
        "punch_type": "OUT"
    })


def test_create_punch(client: TestClient):
    create_sample_punch(client)
    # If API returns data, assert here
