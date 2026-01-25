import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.leave_balance_m import LeaveBalance


# --------------------------------------------------
# BASIC CREATION
# --------------------------------------------------
def test_create_leave_balance_basic(db: Session):
    balance = LeaveBalance(
        user_id=1,
        leave_type_id=1,
        year=2024,
        allocated=12.0,
        used=2.0,
        pending=1.0,
        balance=9.0,
        created_by="test-system"
    )

    db.add(balance)
    db.commit()
    db.refresh(balance)

    assert balance.id is not None
    assert balance.balance == 9.0


# --------------------------------------------------
# UNIQUE CONSTRAINT
# --------------------------------------------------
def test_leave_balance_unique_constraint(db: Session):
    balance1 = LeaveBalance(
        user_id=1,
        leave_type_id=2,
        year=2025,
        allocated=6.0,
        balance=6.0,
        created_by="test-system"
    )

    balance2 = LeaveBalance(
        user_id=1,
        leave_type_id=2,
        year=2025,  # ❌ duplicate (same user + type + year)
        allocated=6.0,
        balance=5.0,
        created_by="test-system"
    )

    db.add(balance1)
    db.commit()

    db.add(balance2)
    with pytest.raises(IntegrityError):
        db.commit()


# --------------------------------------------------
# DIFFERENT YEAR ALLOWED
# --------------------------------------------------
def test_leave_balance_different_year_allowed(db: Session):
    balance_2030 = LeaveBalance(
        user_id=1,
        leave_type_id=1,
        year=2030,
        allocated=12.0,
        balance=12.0,
        created_by="test-system"
    )

    balance_2031 = LeaveBalance(
        user_id=1,
        leave_type_id=1,
        year=2031,
        allocated=12.0,
        balance=12.0,
        created_by="test-system"
    )

    db.add_all([balance_2030, balance_2031])
    db.commit()

    results = db.query(LeaveBalance).filter(
        LeaveBalance.user_id == 1,
        LeaveBalance.leave_type_id == 1,
        LeaveBalance.year.in_([2030, 2031])
    ).all()

    assert len(results) == 2


# --------------------------------------------------
# USAGE FLOW
# --------------------------------------------------
def test_leave_balance_usage_flow(db: Session):
    balance = LeaveBalance(
        user_id=1,
        leave_type_id=2,
        year=2032,
        allocated=10.0,
        used=0.0,
        pending=0.0,
        balance=10.0,
        created_by="test-system"
    )

    db.add(balance)
    db.commit()
    db.refresh(balance)

    balance.used += 2
    balance.balance -= 2
    balance.modified_by = "test-system"
    db.commit()

    assert balance.used == 2
    assert balance.balance == 8


# --------------------------------------------------
# PENDING FLOW
# --------------------------------------------------
def test_leave_balance_pending_flow(db: Session):
    balance = LeaveBalance(
        user_id=1,
        leave_type_id=1,
        year=2033,
        allocated=15.0,
        used=5.0,
        pending=3.0,
        balance=7.0,
        created_by="test-system"
    )

    db.add(balance)
    db.commit()
    db.refresh(balance)

    balance.pending = 0
    balance.used += 3
    balance.balance -= 3
    balance.modified_by = "test-system"
    db.commit()

    assert balance.used == 8
    assert balance.pending == 0
    assert balance.balance == 4
