from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.shift_m import Shift
from app.schema.shift_schema import ShiftCreate, ShiftUpdate, ShiftOut
from app.dependencies import get_current_user
from app.models.user_m import User

# Permission dependencies
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/shifts", tags=["Shifts"])


# ➕ Create Shift
@router.post(
    "/",
    response_model=ShiftOut,
    dependencies=[Depends(require_create_permission(41))]
)
def create_shift(
    shift: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check duplicate shift name
    existing_shift = db.query(Shift).filter(Shift.shift_name == shift.shift_name).first()
    if existing_shift:
        raise HTTPException(status_code=400, detail="Shift with this name already exists")

    # Check duplicate code
    existing_code = db.query(Shift).filter(Shift.shift_code == shift.shift_code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Shift with this code already exists")

    new_shift = Shift(
        shift_name=shift.shift_name,
        description=shift.description,
        start_time=shift.start_time,
        end_time=shift.end_time,
        shift_code=shift.shift_code,
        shift_type=shift.shift_type,
        working_minutes=shift.working_minutes,
        lag_minutes=shift.lag_minutes,
        status=shift.status,
        created_by=current_user.first_name
    )

    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)
    return new_shift


# 📋 Get All Shifts
@router.get(
    "/",
    response_model=List[ShiftOut],
    dependencies=[Depends(require_view_permission(41))]
)
def get_all_shifts(db: Session = Depends(get_db)):
    return db.query(Shift).all()


# 🔍 Get Shift by ID
@router.get(
    "/{shift_id}",
    response_model=ShiftOut,
    dependencies=[Depends(require_view_permission(41))]
)
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


# ✏️ Update Shift
@router.put(
    "/{shift_id}",
    response_model=ShiftOut,
    dependencies=[Depends(require_edit_permission(41))]
)
def update_shift(
    shift_id: int,
    updated_data: ShiftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(shift, key, value)

    shift.modified_by = current_user.first_name

    db.commit()
    db.refresh(shift)
    return shift


# ❌ Delete Shift
@router.delete(
    "/{shift_id}",
    dependencies=[Depends(require_delete_permission(41))]
)
def delete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    db.delete(shift)
    db.commit()

    return {"message": f"Shift deleted successfully by {current_user.first_name}"}
