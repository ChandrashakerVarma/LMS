import pytest
from fastapi.testclient import TestClient


def test_create_holiday(client: TestClient):
    payload = {
        "date": "2025-12-25",
        "name": "Christmas"
    }

    res = client.post("/holidays/", json=payload)
    assert res.status_code == 201  # FIXED
    assert res.json()["name"] == "Christmas"


def test_get_holiday(client: TestClient):
    res = client.get("/holidays/1")
    assert res.status_code == 200
    assert res.json()["id"] == 1


def test_update_holiday(client: TestClient):
    payload = {"name": "Xmas Day"}

    res = client.put("/holidays/1", json=payload)
    assert res.status_code == 200
    assert res.json()["name"] == "Xmas Day"


def test_delete_holiday(client: TestClient):
    res = client.delete("/holidays/1")
    assert res.status_code == 204  # FIXED
