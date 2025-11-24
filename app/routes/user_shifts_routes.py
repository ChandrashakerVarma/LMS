from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user_shifts_m import UserShift
from app.models.user_m import User
from app.models.shift_m import Shift
from app.schema.user_shifts_schema import UserShiftCreate, UserShiftUpdate, UserShiftOut
from app.dependencies import get_current_user

# Permission imports
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/user_shifts", tags=["User Shifts"])

# Menu ID for permission mapping
MENU_ID = 42


# ➕ Assign Shift to User (Create Permission)
@router.post(
    "/",
    response_model=UserShiftOut,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def assign_shift(
    data: UserShiftCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = db.query(Shift).filter(Shift.id == data.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    new_assignment = UserShift(
        **data.dict(exclude_unset=True),
        created_by=current_user.first_name
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment


# 📋 Get All User Shifts (View Permission)
@router.get(
    "/",
    response_model=List[UserShiftOut],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_user_shifts(db: Session = Depends(get_db)):
    return db.query(UserShift).all()


# 🔍 Get User Shift by ID (View Permission)
@router.get(
    "/{assignment_id}",
    response_model=UserShiftOut,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_user_shift(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")
    return assignment


# ✏️ Update User Shift (Edit Permission)
@router.put(
    "/{assignment_id}",
    response_model=UserShiftOut,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_user_shift(
    assignment_id: int,
    data: UserShiftUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(assignment, key, value)

    assignment.modified_by = current_user.first_name

    db.commit()
    db.refresh(assignment)
    return assignment


# ❌ Delete User Shift (Delete Permission)
@router.delete(
    "/{assignment_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
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
