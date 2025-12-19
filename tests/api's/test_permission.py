import pytest
from fastapi.testclient import TestClient


# ------------------------------
# CREATE PERMISSION
# ------------------------------
def test_create_permission(client: TestClient):
    payload = {
        "user_id": 1,
        "shift_id": 1,                     # REQUIRED
        "date": "2025-12-17",
        "from_time": "11:00:00",
        "to_time": "13:00:00",
        "reason": "Doctor Appointment"
    }

    res = client.post("/permissions/", json=payload)
    assert res.status_code == 201
    assert res.json()["reason"] == "Doctor Appointment"
    assert res.json()["shift_id"] == 1


# ------------------------------
# GET PERMISSION BY ID
# ------------------------------
def test_get_permission(client: TestClient):
    res = client.get("/permissions/1")
    assert res.status_code == 200
    assert res.json()["id"] == 1


# ------------------------------
# UPDATE PERMISSION
# ------------------------------
def test_update_permission(client: TestClient):
    payload = {"reason": "Updated Reason"}

    res = client.put("/permissions/1", json=payload)
    assert res.status_code == 200
    assert res.json()["reason"] == "Updated Reason"


# ------------------------------
# DELETE PERMISSION
# ------------------------------
def test_delete_permission(client: TestClient):
    res = client.delete("/permissions/1")
    assert res.status_code == 200
    assert res.json()["message"] == "Permission deleted successfully"
