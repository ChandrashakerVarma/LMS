from fastapi.testclient import TestClient

def create_sample_punch(client):
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


def test_generate_monthly_summary(client: TestClient):
    create_sample_punch(client)

    res = client.post("/attendance-summary/generate/1/2025/12")
    assert res.status_code == 200
    assert res.json()["user_id"] == 1


def test_get_summary_by_user_month(client):
    create_sample_punch(client)
    client.post("/attendance-summary/generate/1/2025/12")

    res = client.get("/attendance-summary/1/2025/12")
    assert res.status_code == 200


def test_get_all_summaries(client):
    create_sample_punch(client)
    client.post("/attendance-summary/generate/1/2025/12")

    res = client.get("/attendance-summary/")
    assert isinstance(res.json(), list)


def test_daily_attendance(client):
    create_sample_punch(client)

    res = client.get("/attendance-summary/daily/1/2025/12")
    assert res.status_code == 200
    assert "days" in res.json()


def test_delete_summary(client):
    create_sample_punch(client)
    client.post("/attendance-summary/generate/1/2025/12")

    res = client.delete("/attendance-summary/delete/1")
    assert res.status_code == 200
