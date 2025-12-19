from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.dependencies import get_current_user
from app.models.leave_balance_m import LeaveBalance
from app.models.leavetype_m import LeaveType
from app.models.user_m import User

from app.schema.leave_balance_schema import (
    LeaveBalanceListResponse,
    LeaveBalanceResponse
)

router = APIRouter(prefix="/leave-balances", tags=["Leave Balances"])

@router.post(
    "/",
    response_model=LeaveBalanceResponse
)
def create_leave_balance(
    user_id: int,
    leave_type_id: int,
    allocated: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    year = date.today().year

    existing = (
        db.query(LeaveBalance)
        .filter_by(
            user_id=user_id,
            leave_type_id=leave_type_id,
            year=year
        )
        .first()
    )

    if existing:
        raise HTTPException(400, "Leave balance already exists")

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
    db.commit()
    db.refresh(balance)

    return balance

@router.get(
    "/me",
    response_model=LeaveBalanceListResponse
)
def get_my_leave_balances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    year = date.today().year

    records = (
        db.query(LeaveBalance, LeaveType)
        .join(LeaveType, LeaveType.id == LeaveBalance.leave_type_id)
        .filter(
            LeaveBalance.user_id == current_user.id,
            LeaveBalance.year == year
        )
        .all()
    )

    return LeaveBalanceListResponse(
        user_id=current_user.id,
        year=year,
        balances=[
            LeaveBalanceResponse(
                leave_type_id=lt.id,
                leave_type=lt.leave_type,
                allocated=lb.allocated,
                used=lb.used,
                pending=lb.pending,
                balance=lb.balance
            )
            for lb, lt in records
        ]
    )

@router.get(
    "/user/{user_id}",
    response_model=LeaveBalanceListResponse
)
def get_user_leave_balances(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    year = date.today().year

    records = (
        db.query(LeaveBalance, LeaveType)
        .join(LeaveType, LeaveType.id == LeaveBalance.leave_type_id)
        .filter(
            LeaveBalance.user_id == user_id,
            LeaveBalance.year == year
        )
        .all()
    )

    return LeaveBalanceListResponse(
        user_id=user_id,
        year=year,
        balances=[
            LeaveBalanceResponse(
                leave_type_id=lt.id,
                leave_type=lt.leave_type,
                allocated=lb.allocated,
                used=lb.used,
                pending=lb.pending,
                balance=lb.balance
            )
            for lb, lt in records
        ]
    )

@router.put(
    "/{balance_id}",
    response_model=LeaveBalanceResponse
)
def update_leave_balance(
    balance_id: int,
    allocated: float | None = None,
    used: float | None = None,
    pending: float | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    balance = db.query(LeaveBalance).filter(LeaveBalance.id == balance_id).first()
    if not balance:
        raise HTTPException(404, "Leave balance not found")

    if allocated is not None:
        balance.allocated = allocated

    if used is not None:
        balance.used = used

    if pending is not None:
        balance.pending = pending

    # ✅ Always recalculate balance
    balance.used = min(balance.used, balance.allocated)
    balance.pending = max(0.0, balance.pending)
    balance.balance = balance.allocated - balance.used

    db.commit()
    db.refresh(balance)
    return balance

@router.delete("/{balance_id}")
def delete_leave_balance(
    balance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    balance = db.query(LeaveBalance).filter(LeaveBalance.id == balance_id).first()
    if not balance:
        raise HTTPException(404, "Leave balance not found")

    db.delete(balance)
    db.commit()
    return {"message": "Leave balance deleted successfully"}
