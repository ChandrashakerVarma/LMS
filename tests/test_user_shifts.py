import pytest
from datetime import date

from app.models.user_shifts_m import UserShift
from app.models.user_m import User
from app.models.shift_m import Shift


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def get_test_user(db):
    user = db.query(User).filter(User.id == 1).first()
    assert user is not None, "Test User not seeded"
    return user


def get_test_shift(db):
    shift = db.query(Shift).filter(Shift.id == 1).first()
    assert shift is not None, "Test Shift not seeded"
    return shift


# --------------------------------------------------
# CREATE USER SHIFT
# --------------------------------------------------
def test_create_user_shift_basic(db):
    user = get_test_user(db)
    shift = get_test_shift(db)

    user_shift = UserShift(
        user_id=user.id,
        shift_id=shift.id,
        assigned_date=date(2025, 1, 1),
        is_active=True,
        created_by="TestUser"
    )

    db.add(user_shift)
    db.commit()
    db.refresh(user_shift)

    assert user_shift.id is not None
    assert user_shift.user_id == user.id
    assert user_shift.shift_id == shift.id
    assert user_shift.is_active is True


# --------------------------------------------------
# UPDATE USER SHIFT
# --------------------------------------------------
def test_update_user_shift(db):
    user = get_test_user(db)
    shift = get_test_shift(db)

    user_shift = UserShift(
        user_id=user.id,
        shift_id=shift.id,
        assigned_date=date(2025, 1, 2),
        is_active=True
    )
    db.add(user_shift)
    db.commit()
    db.refresh(user_shift)

    # Update
    user_shift.is_active = False
    user_shift.modified_by = "AdminUser"
    db.commit()
    db.refresh(user_shift)

    assert user_shift.is_active is False
    assert user_shift.modified_by == "AdminUser"


# --------------------------------------------------
# RELATIONSHIP TEST
# --------------------------------------------------
def test_user_shift_relationships(db):
    user = get_test_user(db)
    shift = get_test_shift(db)

    user_shift = UserShift(
        user_id=user.id,
        shift_id=shift.id,
        assigned_date=date(2025, 1, 3)
    )
    db.add(user_shift)
    db.commit()
    db.refresh(user_shift)

    assert user_shift.user.id == user.id
    assert user_shift.shift.id == shift.id


# --------------------------------------------------
# DELETE USER SHIFT
# --------------------------------------------------
def test_delete_user_shift(db):
    user = get_test_user(db)
    shift = get_test_shift(db)

    user_shift = UserShift(
        user_id=user.id,
        shift_id=shift.id,
        assigned_date=date(2025, 1, 4)
    )
    db.add(user_shift)
    db.commit()

    user_shift_id = user_shift.id

    db.delete(user_shift)
    db.commit()

    deleted = db.query(UserShift).filter_by(id=user_shift_id).first()
    assert deleted is None
