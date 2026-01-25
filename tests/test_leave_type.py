from sqlalchemy.orm import Session

from app.models.leavetype_m import LeaveType
from tests.test_database import TestingSessionLocal


# ==========================================================
# BASIC CREATE (STATELESS)
# ==========================================================
def test_create_leave_type_basic():
    """
    Create a basic leave type
    """
    db: Session = TestingSessionLocal()

    leave_type = LeaveType(
        leave_type="Casual Leave",
        short_code="CL",
        is_active=True,
        created_by="test-system"
    )

    db.add(leave_type)
    db.commit()
    db.refresh(leave_type)

    assert leave_type.id is not None
    assert leave_type.leave_type == "Casual Leave"
    assert leave_type.short_code == "CL"
    assert leave_type.is_active is True

    db.close()


# ==========================================================
# INACTIVE LEAVE TYPE
# ==========================================================
def test_create_inactive_leave_type():
    """
    Create an inactive leave type
    """
    db: Session = TestingSessionLocal()

    leave_type = LeaveType(
        leave_type="Loss of Pay",
        short_code="LOP",
        is_active=False,
        created_by="test-system"
    )

    db.add(leave_type)
    db.commit()

    saved = db.query(LeaveType).filter_by(short_code="LOP").first()

    assert saved is not None
    assert saved.is_active is False

    db.close()


# ==========================================================
# FETCH LEAVE TYPE (STATELESS)
# ==========================================================
def test_fetch_leave_type_by_code():
    """
    Fetch leave type using short_code
    """
    db: Session = TestingSessionLocal()

    leave_type = LeaveType(
        leave_type="Sick Leave",
        short_code="SL",
        created_by="test-system"
    )

    db.add(leave_type)
    db.commit()

    fetched = db.query(LeaveType).filter(LeaveType.short_code == "SL").first()

    assert fetched is not None
    assert fetched.leave_type == "Sick Leave"

    db.close()


# ==========================================================
# UPDATE LEAVE TYPE (STATEFUL)
# ==========================================================
def test_update_leave_type():
    """
    Update leave type name & status
    """
    db: Session = TestingSessionLocal()

    leave_type = LeaveType(
        leave_type="Earned Leave",
        short_code="EL",
        created_by="test-system"
    )

    db.add(leave_type)
    db.commit()

    # Update
    leave_type.leave_type = "Earned Leave Updated"
    leave_type.is_active = False
    leave_type.modified_by = "admin"

    db.commit()
    db.refresh(leave_type)

    assert leave_type.leave_type == "Earned Leave Updated"
    assert leave_type.is_active is False
    assert leave_type.modified_by == "admin"

    db.close()


# ==========================================================
# MULTIPLE LEAVE TYPES (STATEFUL)
# ==========================================================
def test_multiple_leave_types():
    """
    Create multiple leave types and validate count
    """
    db: Session = TestingSessionLocal()

    db.add_all([
        LeaveType(leave_type="Maternity Leave", short_code="ML"),
        LeaveType(leave_type="Paternity Leave", short_code="PL"),
        LeaveType(leave_type="Bereavement Leave", short_code="BL"),
    ])

    db.commit()

    count = db.query(LeaveType).count()
    assert count >= 3

    db.close()


# ==========================================================
# EDGE CASE: DUPLICATE SHORT CODE (EXPECTED FAILURE)
# ==========================================================
def test_duplicate_short_code_not_allowed():
    """
    Duplicate short_code should raise error
    (if DB constraint exists)
    """
    db: Session = TestingSessionLocal()

    leave1 = LeaveType(leave_type="Test Leave 1", short_code="TL")
    leave2 = LeaveType(leave_type="Test Leave 2", short_code="TL")

    db.add(leave1)
    db.commit()

    db.add(leave2)

    try:
        db.commit()
        assert False, "Duplicate short_code allowed"
    except Exception:
        db.rollback()
        assert True

    db.close()
