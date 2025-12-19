from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import List

from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.models.user_m import User

from app.schema.leavemaster_schema import (
    LeaveMasterCreate,
    LeaveMasterUpdate,
    LeaveMasterResponse
)

from app.dependencies import get_current_user

from app.utils.leave_day_util import calculate_leave_days
from app.utils.leave_balance_util import (
    add_pending_leave,
    approve_leave_balance,
    reject_leave_balance
)

MENU_ID = 45

# 🔐 Leave type constants
LOP_LEAVE_TYPE_ID = 8  # Loss of Pay

router = APIRouter(prefix="/leaves", tags=["Leave Master"])


# =================================================
# APPLY LEAVE (SELF / ADMIN FOR OTHERS)
# =================================================
@router.post("/", response_model=LeaveMasterResponse)
def apply_leave(
    data: LeaveMasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    target_user_id = data.user_id or current_user.id

    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    leave_days = calculate_leave_days(
        db,
        data.start_date,
        data.end_date,
        data.is_half_day
    )

    if leave_days <= 0:
        raise HTTPException(status_code=400, detail="Invalid leave duration")

    leave = LeaveMaster(
        user_id=target_user_id,
        leave_type_id=data.leave_type_id,
        start_date=data.start_date,
        end_date=data.end_date,
        is_half_day=data.is_half_day,
        leave_days=leave_days,
        status="pending",
        created_by=current_user.first_name
    )

    db.add(leave)
    db.flush()

    # 🔥 Update pending balance only for paid leaves
    if data.leave_type_id != LOP_LEAVE_TYPE_ID:
        add_pending_leave(
            db,
            target_user_id,
            data.leave_type_id,
            leave_days
        )

    db.commit()
    db.refresh(leave)
    return leave


# =================================================
# UPDATE LEAVE STATUS (ADMIN)
# =================================================
@router.put("/{leave_id}", response_model=LeaveMasterResponse)
def update_leave_status(
    leave_id: int,
    data: LeaveMasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    old_status = leave.status
    new_status = data.status

    if old_status == new_status:
        return leave

    leave.status = new_status
    leave.modified_by = current_user.first_name
    leave.updated_at = datetime.now(UTC)

    # ================= APPROVE =================
    if old_status == "pending" and new_status == "approved":
        if leave.leave_type_id != LOP_LEAVE_TYPE_ID:
            try:
                approve_leave_balance(
                    db,
                    leave.user_id,
                    leave.leave_type_id,
                    leave.leave_days
                )
            except ValueError:
                # 🚨 CL exceeded → convert to LOP
                leave.leave_type_id = LOP_LEAVE_TYPE_ID

    # ================= REJECT / CANCEL =================
    elif old_status == "pending" and new_status in ["rejected", "cancelled"]:
        if leave.leave_type_id != LOP_LEAVE_TYPE_ID:
            reject_leave_balance(
                db,
                leave.user_id,
                leave.leave_type_id,
                leave.leave_days
            )

    db.commit()
    db.refresh(leave)
    return leave


# =================================================
# GET ALL LEAVES
# =================================================
@router.get("/", response_model=List[LeaveMasterResponse])
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(LeaveMaster)
        .order_by(LeaveMaster.created_at.desc())
        .all()
    )


# =================================================
# GET LEAVES BY USER
# =================================================
@router.get("/user/{user_id}", response_model=List[LeaveMasterResponse])
def get_leaves_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(LeaveMaster)
        .filter(LeaveMaster.user_id == user_id)
        .order_by(LeaveMaster.start_date.desc())
        .all()
    )


# =================================================
# GET LEAVE BY ID
# =================================================
@router.get("/{leave_id}", response_model=LeaveMasterResponse)
def get_leave_by_id(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return leave


# =================================================
# DELETE LEAVE
# =================================================
@router.delete("/{leave_id}")
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave.status == "pending" and leave.leave_type_id != LOP_LEAVE_TYPE_ID:
        reject_leave_balance(
            db,
            leave.user_id,
            leave.leave_type_id,
            leave.leave_days
        )

    db.delete(leave)
    db.commit()

    return {"message": "Leave deleted successfully"}
