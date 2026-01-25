from fastapi.testclient import TestClient


def test_create_permission_api(client: TestClient):
    payload = {
        "user_id": 1,
        "shift_id": 1,
        "date": "2025-01-20",
        "reason": "Doctor visit",
        "from_time": "11:00",
        "to_time": "13:00"
    }

    response = client.post("/permissions/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["status"] == "pending"

    # ✅ FIXED (must match FakeUser.first_name)
    assert data["created_by"] == "Test"


def test_create_permission_duplicate_date(client: TestClient):
    payload = {
        "user_id": 1,
        "shift_id": 1,
        "date": "2025-01-21"
    }

    res1 = client.post("/permissions/", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/permissions/", json=payload)
    assert res2.status_code == 400


def test_get_all_permissions(client: TestClient):
    response = client.get("/permissions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_permission_by_id(client: TestClient):
    payload = {
        "user_id": 1,
        "shift_id": 1,
        "date": "2025-01-22"
    }

    create_res = client.post("/permissions/", json=payload)
    permission_id = create_res.json()["id"]

    response = client.get(f"/permissions/{permission_id}")
    assert response.status_code == 200
    assert response.json()["id"] == permission_id


def test_update_permission_status(client: TestClient):
    payload = {
        "user_id": 1,
        "shift_id": 1,
        "date": "2025-01-23"
    }

    create_res = client.post("/permissions/", json=payload)
    permission_id = create_res.json()["id"]

    response = client.put(
        f"/permissions/{permission_id}",
        json={"status": "approved"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_delete_permission(client: TestClient):
    payload = {
        "user_id": 1,
        "shift_id": 1,
        "date": "2025-01-24"
    }

    create_res = client.post("/permissions/", json=payload)
    permission_id = create_res.json()["id"]

    delete_res = client.delete(f"/permissions/{permission_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/permissions/{permission_id}")
    assert get_res.status_code == 404
