# app/routes/attendance_punch_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.attendance_punch_m import AttendancePunch
from app.schema.attendance_punch_schema import (
    AttendancePunchCreate,
    AttendancePunchUpdate,
    AttendancePunchResponse,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/attendance-punch", tags=["Attendance Punch"])


# ----------------------------------------------------
# CREATE Punch Entry
# ----------------------------------------------------
@router.post("/", response_model=AttendancePunchResponse)
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
        created_by=current_user.first_name
    )

    db.add(new_punch)
    db.commit()
    db.refresh(new_punch)

    return new_punch


# ----------------------------------------------------
# GET All Punches
# ----------------------------------------------------
@router.get("/", response_model=List[AttendancePunchResponse])
def get_punches(db: Session = Depends(get_db)):
    return db.query(AttendancePunch).order_by(AttendancePunch.punch_date.desc()).all()


# ----------------------------------------------------
# GET Punch by ID
# ----------------------------------------------------
@router.get("/{punch_id}", response_model=AttendancePunchResponse)
def get_punch(punch_id: int, db: Session = Depends(get_db)):
    punch = db.query(AttendancePunch).filter(AttendancePunch.id == punch_id).first()
    if not punch:
        raise HTTPException(404, "Punch not found")
    return punch


# ----------------------------------------------------
# UPDATE Punch
# ----------------------------------------------------
@router.put("/{punch_id}", response_model=AttendancePunchResponse)
def update_punch(
    punch_id: int,
    data: AttendancePunchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    punch = db.query(AttendancePunch).filter(AttendancePunch.id == punch_id).first()
    if not punch:
        raise HTTPException(404, "Punch not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(punch, key, value)

    punch.modified_by = current_user.first_name

    db.commit()
    db.refresh(punch)
    return punch


# ----------------------------------------------------
# DELETE Punch
# ----------------------------------------------------
@router.delete("/{punch_id}")
def delete_punch(punch_id: int, db: Session = Depends(get_db)):
    punch = db.query(AttendancePunch).filter(AttendancePunch.id == punch_id).first()
    if not punch:
        raise HTTPException(404, "Punch not found")

    db.delete(punch)
    db.commit()

    return {"message": "Punch deleted successfully"}
