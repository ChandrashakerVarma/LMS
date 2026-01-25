from datetime import date
from sqlalchemy.orm import Session

from app.models.leavemaster_m import LeaveMaster
from tests.test_database import TestingSessionLocal


# --------------------------------------------------
# STATELESS TESTS (Independent)
# --------------------------------------------------

def test_create_leave_basic():
    """
    Create a basic leave request (stateless)
    """
    db: Session = TestingSessionLocal()

    leave = LeaveMaster(
        user_id=1,
        leave_type_id=1,          # assume leave_type seeded in test DB
        start_date=date(2025, 1, 10),
        end_date=date(2025, 1, 11),
        leave_days=2.0,
        is_half_day=False,
        status="pending",
        created_by="test-system"
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    assert leave.id is not None
    assert leave.leave_days == 2.0
    assert leave.status == "pending"

    db.close()


def test_create_half_day_leave():
    """
    Create half-day leave (stateless)
    """
    db: Session = TestingSessionLocal()

    leave = LeaveMaster(
        user_id=1,
        leave_type_id=1,
        start_date=date(2025, 1, 12),
        end_date=date(2025, 1, 12),
        leave_days=0.5,
        is_half_day=True,
        status="pending",
        created_by="test-system"
    )

    db.add(leave)
    db.commit()

    saved = (
        db.query(LeaveMaster)
        .filter(
            LeaveMaster.user_id == 1,
            LeaveMaster.start_date == date(2025, 1, 12)
        )
        .first()
    )

    assert saved is not None
    assert saved.is_half_day is True
    assert saved.leave_days == 0.5

    db.close()


# --------------------------------------------------
# STATEFUL TEST (Workflow-like)
# --------------------------------------------------

def test_leave_status_update_flow():
    """
    Pending → Approved → Rejected (stateful)
    """
    db: Session = TestingSessionLocal()

    leave = LeaveMaster(
        user_id=1,
        leave_type_id=1,
        start_date=date(2025, 1, 15),
        end_date=date(2025, 1, 16),
        leave_days=2.0,
        is_half_day=False,
        status="pending",
        created_by="test-system"
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    # Approve leave
    leave.status = "approved"
    leave.modified_by = "manager"
    db.commit()

    assert leave.status == "approved"

    # Reject leave (edge flow)
    leave.status = "rejected"
    leave.modified_by = "admin"
    db.commit()
    db.refresh(leave)

    assert leave.status == "rejected"

    db.close()


# --------------------------------------------------
# EDGE CASE TESTS
# --------------------------------------------------

def test_multiple_leave_requests_same_user():
    """
    Multiple leave requests for same user (allowed)
    """
    db: Session = TestingSessionLocal()

    leave1 = LeaveMaster(
        user_id=1,
        leave_type_id=1,
        start_date=date(2025, 1, 20),
        end_date=date(2025, 1, 20),
        leave_days=1.0,
        status="pending",
        created_by="test-system"
    )

    leave2 = LeaveMaster(
        user_id=1,
        leave_type_id=1,
        start_date=date(2025, 1, 22),
        end_date=date(2025, 1, 23),
        leave_days=2.0,
        status="pending",
        created_by="test-system"
    )

    db.add_all([leave1, leave2])
    db.commit()

    leaves = (
        db.query(LeaveMaster)
        .filter(LeaveMaster.user_id == 1)
        .all()
    )

    assert len(leaves) >= 2

    db.close()


def test_leave_without_end_date():
    """
    Leave with only start date (edge case)
    """
    db: Session = TestingSessionLocal()

    leave = LeaveMaster(
        user_id=1,
        leave_type_id=1,
        start_date=date(2025, 1, 25),
        end_date=None,
        leave_days=1.0,
        status="pending",
        created_by="test-system"
    )

    db.add(leave)
    db.commit()

    saved = (
        db.query(LeaveMaster)
        .filter(LeaveMaster.start_date == date(2025, 1, 25))
        .first()
    )

    assert saved is not None
    assert saved.end_date is None

    db.close()
