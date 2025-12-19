import pytest
from fastapi.testclient import TestClient


# ------------------------------
# CREATE SHIFT
# ------------------------------
def test_create_shift(client: TestClient):
    payload = {
        "shift_name": "Morning Shift",
        "shift_code": "MORN",
        "shift_type": "regular",
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "working_minutes": 480,
        "lag_minutes": 60,
        "description": "Test morning shift",
        "status": "active",
        "is_week_off": 0
    }

    res = client.post("/shifts/", json=payload)
    assert res.status_code == 200
    assert res.json()["shift_name"] == "Morning Shift"


# ------------------------------
# GET SHIFT BY ID
# ------------------------------
def test_get_shift(client: TestClient):
    res = client.get("/shifts/1")
    assert res.status_code == 200
    assert res.json()["id"] == 1


# ------------------------------
# UPDATE SHIFT
# ------------------------------
def test_update_shift(client: TestClient):
    payload = {"shift_name": "Updated Shift"}

    res = client.put("/shifts/1", json=payload)
    assert res.status_code == 200
    assert res.json()["shift_name"] == "Updated Shift"


# ------------------------------
# DELETE SHIFT
# ------------------------------
def test_delete_shift(client: TestClient):
    res = client.delete("/shifts/1")
    assert res.status_code == 200
    assert "deleted successfully" in res.json()["message"]
