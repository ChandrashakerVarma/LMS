import pytest
from datetime import date

from app.models.holiday_m import Holiday


# --------------------------------------------------
# CREATE HOLIDAY (BASIC)
# --------------------------------------------------
def test_create_holiday_basic(db):
    holiday = Holiday(
        date=date(2025, 1, 1),
        name="New Year",
        created_by="TestUser"
    )

    db.add(holiday)
    db.commit()
    db.refresh(holiday)

    assert holiday.id is not None
    assert holiday.date == date(2025, 1, 1)
    assert holiday.name == "New Year"


# --------------------------------------------------
# UNIQUE DATE CONSTRAINT
# --------------------------------------------------
def test_holiday_unique_date(db):
    holiday1 = Holiday(
        date=date(2025, 8, 15),
        name="Independence Day"
    )
    db.add(holiday1)
    db.commit()

    holiday2 = Holiday(
        date=date(2025, 8, 15),
        name="Duplicate Holiday"
    )
    db.add(holiday2)

    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# UPDATE HOLIDAY
# --------------------------------------------------
def test_update_holiday(db):
    holiday = Holiday(
        date=date(2025, 10, 2),
        name="Gandhi Jayanti"
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)

    holiday.name = "Mahatma Gandhi Jayanti"
    holiday.modified_by = "AdminUser"

    db.commit()
    db.refresh(holiday)

    assert holiday.name == "Mahatma Gandhi Jayanti"
    assert holiday.modified_by == "AdminUser"


# --------------------------------------------------
# DELETE HOLIDAY
# --------------------------------------------------
def test_delete_holiday(db):
    holiday = Holiday(
        date=date(2025, 12, 25),
        name="Christmas"
    )
    db.add(holiday)
    db.commit()

    holiday_id = holiday.id

    db.delete(holiday)
    db.commit()

    deleted = db.query(Holiday).filter(
        Holiday.id == holiday_id
    ).first()

    assert deleted is None


# --------------------------------------------------
# HOLIDAY WITHOUT NAME (ALLOWED)
# --------------------------------------------------
def test_holiday_without_name(db):
    holiday = Holiday(
        date=date(2025, 11, 14)  # Children's Day
    )

    db.add(holiday)
    db.commit()
    db.refresh(holiday)

    assert holiday.id is not None
    assert holiday.name is None
