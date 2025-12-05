from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.user_shifts_m import UserShift
from app.models.user_m import User
from app.models.shift_roster_detail_m import ShiftRosterDetail

from app.schema.user_shifts_schema import (
    UserShiftCreate,
    UserShiftUpdate,
    UserShiftResponse
)

from app.dependencies import get_current_user

# Permission Imports
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/user_shifts", tags=["User Shifts"])

MENU_ID = 42


# ➕ Assign Shift Automatically From Roster
@router.post(
    "/",
    response_model=UserShiftResponse,
    dependencies=[Depends(require_create_permission(MENU_ID))],
    operation_id="assign_shift_to_user"
)
def assign_shift(
    user_shift: UserShiftCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Validate User
    user = db.query(User).filter(User.id == user_shift.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.shift_roster_id:
        raise HTTPException(status_code=400, detail="User does not have a shift roster assigned")

    weekday = user_shift.assigned_date.isoweekday()

    roster_detail = db.query(ShiftRosterDetail).filter(
        ShiftRosterDetail.shift_roster_id == user.shift_roster_id,
        ShiftRosterDetail.week_day_id == weekday
    ).first()

    if not roster_detail:
        raise HTTPException(
            status_code=404,
            detail=f"No shift found in roster for weekday {weekday}"
        )

    new_assignment = UserShift(
        user_id=user_shift.user_id,
        shift_id=roster_detail.shift_id,
        assigned_date=user_shift.assigned_date,
        created_by=current_user.first_name
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment


# 📋 Get All User Shifts
@router.get(
    "/",
    response_model=List[UserShiftResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))],
    operation_id="get_all_user_shifts_list"
)
def get_all_user_shifts(db: Session = Depends(get_db)):
    return db.query(UserShift).all()


# 🔍 Get Single User Shift
@router.get(
    "/{assignment_id}",
    response_model=UserShiftResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))],
    operation_id="get_user_shift_record"
)
def get_user_shift(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")
    return assignment


# ✏️ Update User Shift
@router.put(
    "/{assignment_id}",
    response_model=UserShiftResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))],
    operation_id="update_user_shift_record"
)
def update_user_shift(
    assignment_id: int,
    updated_data: UserShiftUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")

    # Reassign shift if date changed
    if updated_data.assigned_date:
        user = db.query(User).filter(User.id == assignment.user_id).first()

        weekday = updated_data.assigned_date.isoweekday()

        roster_detail = db.query(ShiftRosterDetail).filter(
            ShiftRosterDetail.shift_roster_id == user.shift_roster_id,
            ShiftRosterDetail.week_day_id == weekday
        ).first()

        if not roster_detail:
            raise HTTPException(
                status_code=404,
                detail=f"No shift found for weekday {weekday} in user's roster"
            )

        assignment.shift_id = roster_detail.shift_id
        assignment.assigned_date = updated_data.assigned_date

    # Update is_active
    if updated_data.is_active is not None:
        assignment.is_active = updated_data.is_active

    assignment.modified_by = current_user.first_name

    db.commit()
    db.refresh(assignment)

    return assignment


# ❌ Delete User Shift
@router.delete(
    "/{assignment_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))],
    operation_id="delete_user_shift_record"
)
def delete_user_shift(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")

    db.delete(assignment)
    db.commit()

    return {
        "message": "User shift deleted successfully",
        "deleted_by": current_user.first_name
    }
