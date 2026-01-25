from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from calendar import monthrange

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


# =====================================================
# ➕ ASSIGN SHIFT FOR A SINGLE DAY (Existing Logic)
# =====================================================
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


# =====================================================
# ➕ ASSIGN SHIFTS FOR A FULL MONTH (NEW)
# =====================================================
@router.post(
    "/assign-month/{user_id}/{year}/{month}",
    dependencies=[Depends(require_create_permission(MENU_ID))],
    operation_id="assign_shift_for_month"
)
def assign_shift_for_month(
    user_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.shift_roster_id:
        raise HTTPException(status_code=400, detail="Invalid user or shift roster")

    days_in_month = monthrange(year, month)[1]
    created = 0

    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.isoweekday()

        roster_detail = db.query(ShiftRosterDetail).filter(
            ShiftRosterDetail.shift_roster_id == user.shift_roster_id,
            ShiftRosterDetail.week_day_id == weekday
        ).first()

        if not roster_detail:
            continue

        exists = db.query(UserShift).filter(
            UserShift.user_id == user_id,
            UserShift.assigned_date == current_date
        ).first()

        if exists:
            continue

        db.add(UserShift(
            user_id=user_id,
            shift_id=roster_detail.shift_id,
            assigned_date=current_date,
            created_by=current_user.first_name
        ))
        created += 1

    db.commit()

    return {
        "message": "Monthly shifts assigned successfully",
        "records_created": created
    }


# =====================================================
# 📋 GET ALL USER SHIFTS
# =====================================================
@router.get(
    "/",
    response_model=List[UserShiftResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))],
    operation_id="get_all_user_shifts_list"
)
def get_all_user_shifts(db: Session = Depends(get_db)):
    return db.query(UserShift).all()


# =====================================================
# 📅 GET USER SHIFTS FOR A MONTH (NEW)
# =====================================================
@router.get(
    "/user/{user_id}/{year}/{month}",
    response_model=List[UserShiftResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))],
    operation_id="get_user_shifts_for_month"
)
def get_user_shifts_for_month(
    user_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])

    return db.query(UserShift).filter(
        UserShift.user_id == user_id,
        UserShift.assigned_date.between(start_date, end_date)
    ).all()


# =====================================================
# 🔍 GET SINGLE USER SHIFT
# =====================================================
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


# =====================================================
# ✏️ UPDATE USER SHIFT
# =====================================================
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
                detail=f"No shift found for weekday {weekday}"
            )

        assignment.shift_id = roster_detail.shift_id
        assignment.assigned_date = updated_data.assigned_date

    if updated_data.is_active is not None:
        assignment.is_active = updated_data.is_active

    assignment.modified_by = current_user.first_name
    db.commit()
    db.refresh(assignment)

    return assignment


# =====================================================
# ❌ DELETE USER SHIFT
# =====================================================
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
