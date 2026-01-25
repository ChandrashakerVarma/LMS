import pytest

from app.models.shift_roster_m import ShiftRoster


# --------------------------------------------------
# CREATE SHIFT ROSTER (BASIC)
# --------------------------------------------------
def test_create_shift_roster_basic(db):
    roster = ShiftRoster(
        name="Morning Roster",
        created_by="TestUser"
    )

    db.add(roster)
    db.commit()
    db.refresh(roster)

    assert roster.id is not None
    assert roster.name == "Morning Roster"
    assert roster.is_active is True


# --------------------------------------------------
# UNIQUE NAME CONSTRAINT
# --------------------------------------------------
def test_shift_roster_unique_name(db):
    roster1 = ShiftRoster(
        name="Unique Roster",
        created_by="TestUser"
    )
    db.add(roster1)
    db.commit()

    roster2 = ShiftRoster(
        name="Unique Roster",
        created_by="TestUser"
    )
    db.add(roster2)

    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# UPDATE SHIFT ROSTER
# --------------------------------------------------
def test_update_shift_roster(db):
    roster = ShiftRoster(
        name="Update Roster",
        created_by="TestUser"
    )
    db.add(roster)
    db.commit()
    db.refresh(roster)

    roster.name = "Updated Roster Name"
    roster.is_active = False
    roster.modified_by = "AdminUser"

    db.commit()
    db.refresh(roster)

    assert roster.name == "Updated Roster Name"
    assert roster.is_active is False
    assert roster.modified_by == "AdminUser"


# --------------------------------------------------
# RELATIONSHIP PLACEHOLDER TEST
# (details & users handled in their own tests)
# --------------------------------------------------
def test_shift_roster_relationships(db):
    roster = ShiftRoster(
        name="Relation Roster",
        created_by="TestUser"
    )
    db.add(roster)
    db.commit()
    db.refresh(roster)

    assert roster.shift_roster_details == []
    assert roster.users == []


# --------------------------------------------------
# DELETE SHIFT ROSTER
# --------------------------------------------------
def test_delete_shift_roster(db):
    roster = ShiftRoster(
        name="Delete Roster",
        created_by="TestUser"
    )
    db.add(roster)
    db.commit()

    roster_id = roster.id

    db.delete(roster)
    db.commit()

    deleted = db.query(ShiftRoster).filter(
        ShiftRoster.id == roster_id
    ).first()

    assert deleted is None
