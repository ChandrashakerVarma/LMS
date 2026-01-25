import pytest

from app.models.shift_roster_m import ShiftRoster
from app.models.shift_roster_detail_m import ShiftRosterDetail
from app.models.week_day_m import WeekDay
from app.models.shift_m import Shift


# --------------------------------------------------
# HELPER: GET OR CREATE WEEKDAY (TEST-SAFE)
# --------------------------------------------------
def get_or_create_weekday(db, week_name="Monday"):
    weekday = db.query(WeekDay).filter_by(week_name=week_name).first()
    if weekday:
        return weekday

    weekday = WeekDay(
        week_name=week_name
    )
    db.add(weekday)
    db.commit()
    db.refresh(weekday)
    return weekday


# --------------------------------------------------
# CREATE SHIFT ROSTER DETAIL
# --------------------------------------------------
def test_create_shift_roster_detail_basic(db):
    roster = ShiftRoster(
        name="Weekly Roster Detail",
        created_by="TestUser"
    )
    db.add(roster)
    db.commit()
    db.refresh(roster)

    weekday = get_or_create_weekday(db, "Monday")

    shift = db.query(Shift).filter(Shift.id == 1).first()
    assert shift is not None

    detail = ShiftRosterDetail(
        shift_roster_id=roster.id,
        week_day_id=weekday.id,
        shift_id=shift.id,
        created_by="TestUser"
    )

    db.add(detail)
    db.commit()
    db.refresh(detail)

    assert detail.id is not None
    assert detail.week_day_id == weekday.id
    assert detail.shift_id == shift.id


# --------------------------------------------------
# UPDATE SHIFT ROSTER DETAIL
# --------------------------------------------------
def test_update_shift_roster_detail(db):
    roster = ShiftRoster(
        name="Update Roster Detail",
        created_by="TestUser"
    )
    db.add(roster)
    db.commit()
    db.refresh(roster)

    weekday = get_or_create_weekday(db, "Tuesday")
    shift = db.query(Shift).filter(Shift.id == 1).first()

    detail = ShiftRosterDetail(
        shift_roster_id=roster.id,
        week_day_id=weekday.id,
        shift_id=shift.id
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)

    detail.modified_by = "AdminUser"
    db.commit()
    db.refresh(detail)

    assert detail.modified_by == "AdminUser"


# --------------------------------------------------
# RELATIONSHIP TEST
# --------------------------------------------------
def test_shift_roster_detail_relationships(db):
    roster = ShiftRoster(
        name="Relation Roster Detail",
        created_by="TestUser"
    )
    db.add(roster)
    db.commit()
    db.refresh(roster)

    weekday = get_or_create_weekday(db, "Wednesday")
    shift = db.query(Shift).filter(Shift.id == 1).first()

    detail = ShiftRosterDetail(
        shift_roster_id=roster.id,
        week_day_id=weekday.id,
        shift_id=shift.id
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)

    assert detail.shift_roster.id == roster.id
    assert detail.week_day.week_name == "Wednesday"
    assert detail.shift.id == shift.id


# --------------------------------------------------
# DELETE SHIFT ROSTER DETAIL
# --------------------------------------------------
def test_delete_shift_roster_detail(db):
    roster = ShiftRoster(
        name="Delete Roster Detail",
        created_by="TestUser"
    )
    db.add(roster)
    db.commit()
    db.refresh(roster)

    weekday = get_or_create_weekday(db, "Thursday")
    shift = db.query(Shift).filter(Shift.id == 1).first()

    detail = ShiftRosterDetail(
        shift_roster_id=roster.id,
        week_day_id=weekday.id,
        shift_id=shift.id
    )
    db.add(detail)
    db.commit()

    detail_id = detail.id

    db.delete(detail)
    db.commit()

    deleted = db.query(ShiftRosterDetail).filter_by(id=detail_id).first()
    assert deleted is None
