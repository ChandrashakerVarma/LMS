from datetime import date
from sqlalchemy.orm import Session

from app.models.leave_balance_m import LeaveBalance
from app.models.leaveconfig_m import LeaveConfig


# ==================================================
# CONSTANTS
# ==================================================
# ⚠️ Must match Loss of Pay ID in leave_types table
LOP_LEAVE_TYPE_ID = 8


# ==================================================
# Get or create leave balance row
# ==================================================
def get_or_create_leave_balance(
    db: Session,
    user_id: int,
    leave_type_id: int,
    year: int
) -> LeaveBalance:

    balance = (
        db.query(LeaveBalance)
        .filter_by(
            user_id=user_id,
            leave_type_id=leave_type_id,
            year=year
        )
        .first()
    )

    if balance:
        return balance

    config = (
        db.query(LeaveConfig)
        .filter(LeaveConfig.leave_type_id == leave_type_id)
        .first()
    )

    allocated = float(config.no_of_leaves) if config else 0.0

    balance = LeaveBalance(
        user_id=user_id,
        leave_type_id=leave_type_id,
        year=year,
        allocated=allocated,
        used=0.0,
        pending=0.0,
        balance=allocated
    )

    db.add(balance)
    db.flush()
    return balance


# ==================================================
# When leave is APPLIED (PENDING)
# ==================================================
def add_pending_leave(
    db: Session,
    user_id: int,
    leave_type_id: int,
    leave_days: float
):
    year = date.today().year
    lb = get_or_create_leave_balance(db, user_id, leave_type_id, year)

    lb.pending += leave_days
    db.flush()


# ==================================================
# When leave is APPROVED
# ==================================================
def approve_leave_balance(
    db: Session,
    user_id: int,
    leave_type_id: int,
    leave_days: float
):
    year = date.today().year

    # --------------------------------------------------
    # CASE 1: LOP itself (no allocation logic)
    # --------------------------------------------------
    if leave_type_id == LOP_LEAVE_TYPE_ID:
        lop = get_or_create_leave_balance(
            db, user_id, LOP_LEAVE_TYPE_ID, year
        )
        lop.used += leave_days
        lop.balance = 0.0
        db.flush()
        return

    # --------------------------------------------------
    # CASE 2: Paid leave (CL / SL / EL)
    # --------------------------------------------------
    lb = get_or_create_leave_balance(
        db, user_id, leave_type_id, year
    )

    available = lb.allocated - lb.used

    # ✅ Fully covered by paid leave
    if leave_days <= available:
        lb.pending = max(0.0, lb.pending - leave_days)
        lb.used += leave_days
        lb.balance = lb.allocated - lb.used
        db.flush()
        return

    # --------------------------------------------------
    # PARTIAL → Convert excess to LOP
    # --------------------------------------------------
    paid_part = max(0.0, available)
    lop_part = leave_days - paid_part

    # Update paid leave
    if paid_part > 0:
        lb.used += paid_part

    lb.pending = max(0.0, lb.pending - leave_days)
    lb.balance = max(0.0, lb.allocated - lb.used)

    # Create / update LOP
    lop = get_or_create_leave_balance(
        db, user_id, LOP_LEAVE_TYPE_ID, year
    )
    lop.used += lop_part
    lop.balance = 0.0

    db.flush()


# ==================================================
# When leave is REJECTED / CANCELLED
# ==================================================
def reject_leave_balance(
    db: Session,
    user_id: int,
    leave_type_id: int,
    leave_days: float
):
    year = date.today().year
    lb = get_or_create_leave_balance(db, user_id, leave_type_id, year)

    lb.pending = max(0.0, lb.pending - leave_days)
    db.flush()
