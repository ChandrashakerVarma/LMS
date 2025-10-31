from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.attendance_m import Attendance
from app.schema.attendance_schema import AttendanceCreate, AttendanceOut, AttendanceUpdate

router = APIRouter(prefix="/attendances", tags=["Attendances"])


# ➕ Create Attendance
@router.post("/", response_model=AttendanceOut)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    new_attendance = Attendance(**attendance.dict())
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance


# 📋 Get All Attendances
@router.get("/", response_model=List[AttendanceOut])
def get_all_attendances(db: Session = Depends(get_db)):
    return db.query(Attendance).all()


# 🔍 Get Attendance by ID
@router.get("/{attendance_id}", response_model=AttendanceOut)
def get_attendance_by_id(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


# ✏️ Update Attendance
@router.put("/{attendance_id}", response_model=AttendanceOut)
def update_attendance(attendance_id: int, update_data: AttendanceUpdate, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(attendance, key, value)
    attendance.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(attendance)
    return attendance


# ❌ Delete Attendance
@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    db.delete(attendance)
    db.commit()
    return {"message": "Attendance deleted successfully"}
