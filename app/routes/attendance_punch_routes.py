# app/routes/attendance_punch_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.attendance_punch_m import AttendancePunch

# ✔ Correct schemas import folder (schemas NOT schema)
from app.schemas.attendance_punch_schema import (
    AttendancePunchCreate,
    AttendancePunchUpdate,
    AttendancePunchResponse,
)

# Dependencies
from app.dependencies import get_current_user

# Permission dependencies
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

# Unique menu ID
ATTENDANCE_PUNCH_MENU_ID = 46

router = APIRouter(prefix="/attendance-punch", tags=["Attendance Punch"])


# ----------------------- CREATE -----------------------
@router.post(
    "/",
    response_model=AttendancePunchResponse,
    dependencies=[Depends(require_create_permission(ATTENDANCE_PUNCH_MENU_ID))]
)
def create_punch(
    data: AttendancePunchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_punch = AttendancePunch(
        bio_id=data.bio_id,
        punch_date=data.punch_date,
        punch_time=data.punch_time,
        punch_type=data.punch_type,
        created_by=current_user.first_name,
    )

    db.add(new_punch)
    db.commit()
    db.refresh(new_punch)
    return new_punch


# ----------------------- LIST ALL -----------------------
@router.get(
    "/",
    response_model=List[AttendancePunchResponse],
    dependencies=[Depends(require_view_permission(ATTENDANCE_PUNCH_MENU_ID))]
)
def get_punches(db: Session = Depends(get_db)):
    return db.query(AttendancePunch).order_by(
        AttendancePunch.punch_date.desc()
    ).all()


# ----------------------- GET SINGLE -----------------------
@router.get(
    "/{punch_id}",
    response_model=AttendancePunchResponse,
    dependencies=[Depends(require_view_permission(ATTENDANCE_PUNCH_MENU_ID))]
)
def get_punch(punch_id: int, db: Session = Depends(get_db)):
    punch = db.query(AttendancePunch).filter(
        AttendancePunch.id == punch_id
    ).first()

    if not punch:
        raise HTTPException(status_code=404, detail="Punch not found")

    return punch


# ----------------------- UPDATE -----------------------
@router.put(
    "/{punch_id}",
    response_model=AttendancePunchResponse,
    dependencies=[Depends(require_edit_permission(ATTENDANCE_PUNCH_MENU_ID))]
)
def update_punch(
    punch_id: int,
    data: AttendancePunchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    punch = db.query(AttendancePunch).filter(
        AttendancePunch.id == punch_id
    ).first()

    if not punch:
        raise HTTPException(status_code=404, detail="Punch not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(punch, key, value)

    punch.modified_by = current_user.first_name
    db.commit()
    db.refresh(punch)
    return punch


# ----------------------- DELETE -----------------------
@router.delete(
    "/{punch_id}",
    dependencies=[Depends(require_delete_permission(ATTENDANCE_PUNCH_MENU_ID))]
)
def delete_punch(
    punch_id: int,
    db: Session = Depends(get_db)
):
    punch = db.query(AttendancePunch).filter(
        AttendancePunch.id == punch_id
    ).first()

    if not punch:
        raise HTTPException(status_code=404, detail="Punch not found")

    db.delete(punch)
    db.commit()
    return {"message": "Punch deleted successfully"}
