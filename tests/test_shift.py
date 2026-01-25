import pytest
from datetime import time

from app.models.shift_m import Shift


# --------------------------------------------------
# CREATE SHIFT (BASIC)
# --------------------------------------------------
def test_create_shift_basic(db):
    shift = Shift(
        created_by=1,
        shift_name="Test Shift A",     # ✅ UNIQUE
        shift_code="TST_A",            # ✅ UNIQUE
        shift_type="regular",
        start_time=time(9, 0),
        end_time=time(17, 0),
        working_minutes=480,
        lag_minutes=60,
        status="active",
        is_week_off=0
    )

    db.add(shift)
    db.commit()
    db.refresh(shift)

    assert shift.id is not None
    assert shift.shift_name == "Test Shift A"
    assert shift.shift_code == "TST_A"


# --------------------------------------------------
# UNIQUE SHIFT NAME CONSTRAINT
# --------------------------------------------------
def test_shift_unique_name(db):
    shift1 = Shift(
        created_by=1,
        shift_name="Unique Shift Name",
        shift_code="UNQ1",
        start_time=time(6, 0),
        end_time=time(14, 0),
        working_minutes=480
    )

    db.add(shift1)
    db.commit()

    shift2 = Shift(
        created_by=1,
        shift_name="Unique Shift Name",   # ❌ duplicate
        shift_code="UNQ2",
        start_time=time(7, 0),
        end_time=time(15, 0),
        working_minutes=480
    )

    db.add(shift2)

    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# UNIQUE SHIFT CODE CONSTRAINT
# --------------------------------------------------
def test_shift_unique_code(db):
    shift1 = Shift(
        created_by=1,
        shift_name="Evening Shift X",
        shift_code="EVX",
        start_time=time(14, 0),
        end_time=time(22, 0),
        working_minutes=480
    )

    db.add(shift1)
    db.commit()

    shift2 = Shift(
        created_by=1,
        shift_name="Evening Shift Y",
        shift_code="EVX",              # ❌ duplicate code
        start_time=time(15, 0),
        end_time=time(23, 0),
        working_minutes=480
    )

    db.add(shift2)

    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# DEFAULT VALUES
# --------------------------------------------------
def test_shift_default_values(db):
    shift = Shift(
        created_by=1,
        shift_name="Default Shift X",
        shift_code="DFX",
        start_time=time(10, 0),
        end_time=time(18, 0),
        working_minutes=480
    )

    db.add(shift)
    db.commit()
    db.refresh(shift)

    assert shift.lag_minutes == 60
    assert shift.status == "active"
    assert shift.is_week_off == 0


# --------------------------------------------------
# UPDATE SHIFT
# --------------------------------------------------
def test_update_shift(db):
    shift = Shift(
        created_by=1,
        shift_name="Update Shift X",
        shift_code="UPX",
        start_time=time(9, 0),
        end_time=time(17, 0),
        working_minutes=480
    )

    db.add(shift)
    db.commit()
    db.refresh(shift)

    shift.shift_name = "Updated Shift X"
    shift.status = "inactive"
    shift.modified_by = "AdminUser"

    db.commit()
    db.refresh(shift)

    assert shift.shift_name == "Updated Shift X"
    assert shift.status == "inactive"


# --------------------------------------------------
# DELETE SHIFT
# --------------------------------------------------
def test_delete_shift(db):
    shift = Shift(
        created_by=1,
        shift_name="Delete Shift X",
        shift_code="DLX",
        start_time=time(8, 0),
        end_time=time(16, 0),
        working_minutes=480
    )

    db.add(shift)
    db.commit()

    shift_id = shift.id

    db.delete(shift)
    db.commit()

    deleted = db.query(Shift).filter(
        Shift.id == shift_id
    ).first()

    assert deleted is None
