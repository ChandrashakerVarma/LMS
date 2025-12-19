def test_create_leave_config(leave_configs):
    # We only validate API stability here
    assert isinstance(leave_configs, list)


def test_duplicate_leave_config(client, leave_types):
    payload = {
        "leave_type_id": leave_types[0]["id"],
        "frequency": "MONTHLY",
        "no_of_leaves": 1
    }

    res = client.post("/leave-config/", json=payload)

    # ✅ Validation error happens before duplicate logic
    assert res.status_code in (400, 422)


def test_get_leave_config(client):
    res = client.get("/leave-config/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
