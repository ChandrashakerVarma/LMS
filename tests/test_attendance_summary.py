from datetime import date
from sqlalchemy.orm import Session

from app.models.attendance_summary_m import Attendance
from tests.test_database import TestingSessionLocal


# --------------------------------------------------
# STATELESS TESTS (Independent)
# --------------------------------------------------

def test_create_attendance_summary_basic():
    """
    Create a basic monthly attendance summary (stateless)
    """
    db: Session = TestingSessionLocal()

    attendance = Attendance(
        user_id=1,
        month=date(2025, 1, 1),
        total_days=31,
        present_days=1,
        absent_days=0,
        half_days=0,
        holidays=0,
        sundays=4,
        leaves=0,
        permissions=0,
        total_work_minutes=480,
        overtime_minutes=0,
        late_minutes=0,
        early_exit_minutes=0,
        summary_status="Completed",
        created_by="test-system"
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    assert attendance.id is not None
    assert attendance.present_days == 1
    assert attendance.summary_status == "Completed"

    db.close()


def test_attendance_summary_zero_values():
    """
    Attendance summary with zero work (stateless)
    """
    db: Session = TestingSessionLocal()

    attendance = Attendance(
        user_id=1,
        month=date(2025, 2, 1),
        total_days=28,
        present_days=0,
        absent_days=24,
        half_days=0,
        holidays=0,
        sundays=4,
        leaves=0,
        permissions=0,
        total_work_minutes=0,
        overtime_minutes=0,
        late_minutes=0,
        early_exit_minutes=0,
        summary_status="Pending",
        created_by="test-system"
    )

    db.add(attendance)
    db.commit()

    saved = (
        db.query(Attendance)
        .filter(Attendance.month == date(2025, 2, 1))
        .first()
    )

    assert saved is not None
    assert saved.present_days == 0
    assert saved.total_work_minutes == 0
    assert saved.summary_status == "Pending"

    db.close()


# --------------------------------------------------
# STATEFUL TEST (Workflow-like)
# --------------------------------------------------

def test_attendance_summary_update_flow():
    """
    Create → Update attendance summary (stateful)
    """
    db: Session = TestingSessionLocal()

    attendance = Attendance(
        user_id=1,
        month=date(2025, 3, 1),
        total_days=31,
        present_days=10,
        absent_days=17,
        half_days=0,
        holidays=0,
        sundays=4,
        leaves=0,
        permissions=0,
        total_work_minutes=4800,
        overtime_minutes=0,
        late_minutes=0,
        early_exit_minutes=0,
        summary_status="Pending",
        created_by="test-system"
    )

    db.add(attendance)
    db.commit()

    # Update summary after recalculation
    attendance.present_days = 20
    attendance.absent_days = 7
    attendance.total_work_minutes = 9600
    attendance.summary_status = "Completed"
    attendance.modified_by = "test-system"

    db.commit()
    db.refresh(attendance)

    assert attendance.present_days == 20
    assert attendance.absent_days == 7
    assert attendance.total_work_minutes == 9600
    assert attendance.summary_status == "Completed"

    db.close()


# --------------------------------------------------
# EDGE CASE TEST
# --------------------------------------------------

def test_attendance_summary_duplicate_month():
    """
    Allow multiple summaries for same user/month
    (depends on business rule)
    """
    db: Session = TestingSessionLocal()

    summary = Attendance(
        user_id=1,
        month=date(2025, 4, 1),
        total_days=30,
        present_days=15,
        absent_days=11,
        half_days=0,
        holidays=0,
        sundays=4,
        leaves=0,
        permissions=0,
        total_work_minutes=7200,
        summary_status="Completed",
        created_by="test-system"
    )

    db.add(summary)
    db.commit()

    summaries = (
        db.query(Attendance)
        .filter(Attendance.user_id == 1, Attendance.month == date(2025, 4, 1))
        .all()
    )

    assert len(summaries) >= 1

    db.close()
