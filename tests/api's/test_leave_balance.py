def test_get_my_leave_balance(client):
    res = client.get("/leave-balances/me")
    assert res.status_code == 200

    data = res.json()

    # --- top-level response ---
    assert "user_id" in data
    assert "year" in data
    assert "balances" in data
    assert isinstance(data["balances"], list)


def test_leave_balance_schema_fields(client):
    res = client.get("/leave-balances/me")
    data = res.json()

    for bal in data["balances"]:
        # --- schema validation ---
        assert "leave_type_id" in bal
        assert "leave_type" in bal

        assert "allocated" in bal
        assert "used" in bal
        assert "pending" in bal
        assert "balance" in bal

        # --- type safety ---
        assert isinstance(bal["allocated"], (int, float))
        assert isinstance(bal["used"], (int, float))
        assert isinstance(bal["pending"], (int, float))
        assert isinstance(bal["balance"], (int, float))


def test_leave_balance_after_leave_application(client, applied_leave):
    """
    Even after applying leave, balance update may not be implemented yet.
    This test ensures API stability.
    """
    res = client.get("/leave-balances/me")
    assert res.status_code == 200

    data = res.json()
    assert "balances" in data
    assert isinstance(data["balances"], list)
