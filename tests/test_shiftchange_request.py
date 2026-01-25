import pytest
from datetime import date, time

from app.models.shift_change_request_m import ShiftChangeRequest
from app.models.shift_m import Shift


# --------------------------------------------------
# CREATE SHIFT CHANGE REQUEST (BASIC)
# --------------------------------------------------
def test_create_shift_change_request_basic(db):
    # Create NEW shift (not seeded)
    new_shift = Shift(
        created_by=1,
        shift_name="SCR Shift A",
        shift_code="SCR_A",
        shift_type="regular",
        start_time=time(10, 0),
        end_time=time(18, 0),
        working_minutes=480
    )
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    request = ShiftChangeRequest(
        user_id=1,
        old_shift_id=1,               # seeded shift
        new_shift_id=new_shift.id,
        request_date=date.today(),
        reason="Need different working hours",
        created_by="TestUser"
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    assert request.id is not None
    assert request.status == "Pending"
    assert request.user_id == 1
    assert request.new_shift_id == new_shift.id


# --------------------------------------------------
# DEFAULT STATUS SHOULD BE PENDING
# --------------------------------------------------
def test_shift_change_request_default_status(db):
    shift = Shift(
        created_by=1,
        shift_name="SCR Shift B",
        shift_code="SCR_B",
        start_time=time(8, 0),
        end_time=time(16, 0),
        working_minutes=480
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    request = ShiftChangeRequest(
        user_id=1,
        new_shift_id=shift.id,
        request_date=date.today()
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    assert request.status == "Pending"


# --------------------------------------------------
# UPDATE STATUS FLOW
# --------------------------------------------------
def test_shift_change_request_status_update(db):
    shift = Shift(
        created_by=1,
        shift_name="SCR Shift C",
        shift_code="SCR_C",
        start_time=time(12, 0),
        end_time=time(20, 0),
        working_minutes=480
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    request = ShiftChangeRequest(
        user_id=1,
        new_shift_id=shift.id,
        request_date=date.today(),
        created_by="TestUser"
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    # Update status
    request.status = "Approved"
    request.modified_by = "ManagerUser"

    db.commit()
    db.refresh(request)

    assert request.status == "Approved"
    assert request.modified_by == "ManagerUser"


# --------------------------------------------------
# RELATIONSHIP TEST
# --------------------------------------------------
def test_shift_change_request_relationships(db):
    shift = Shift(
        created_by=1,
        shift_name="SCR Shift D",
        shift_code="SCR_D",
        start_time=time(6, 0),
        end_time=time(14, 0),
        working_minutes=480
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    request = ShiftChangeRequest(
        user_id=1,
        new_shift_id=shift.id,
        request_date=date.today()
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    assert request.user is not None
    assert request.new_shift.shift_name == "SCR Shift D"


# --------------------------------------------------
# DELETE SHIFT CHANGE REQUEST
# --------------------------------------------------
def test_delete_shift_change_request(db):
    shift = Shift(
        created_by=1,
        shift_name="SCR Shift E",
        shift_code="SCR_E",
        start_time=time(7, 0),
        end_time=time(15, 0),
        working_minutes=480
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    request = ShiftChangeRequest(
        user_id=1,
        new_shift_id=shift.id,
        request_date=date.today()
    )

    db.add(request)
    db.commit()

    request_id = request.id

    db.delete(request)
    db.commit()

    deleted = db.query(ShiftChangeRequest).filter(
        ShiftChangeRequest.id == request_id
    ).first()

    assert deleted is None
