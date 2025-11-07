from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.attendance_m import Attendance
from app.models.shift_m import Shift
from app.schema.attendance_schema import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.utils.attendance_utils import calculate_attendance_status

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# CREATE Attendance
@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == payload.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    if payload.punch_in >= payload.punch_out:
        raise HTTPException(status_code=400, detail="Punch-out must be after punch-in")

    result = calculate_attendance_status(
        shift_start=shift.start_time,
        shift_end=shift.end_time,
        lag_minutes=shift.lag_minutes,
        working_minutes=shift.working_minutes,
        punch_in=payload.punch_in,
        punch_out=payload.punch_out
    )

    attendance = Attendance(
        user_id=payload.user_id,
        shift_id=payload.shift_id,
        punch_in=payload.punch_in,
        punch_out=payload.punch_out,
        total_worked_minutes=result["total_worked_minutes"],
        status=result["status"]
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


# GET all attendance
@router.get("/", response_model=List[AttendanceResponse])
def get_all_attendance(db: Session = Depends(get_db)):
    return db.query(Attendance).all()


# GET by ID
@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return record


# UPDATE attendance
@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, payload: AttendanceUpdate, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")

    # Update punch_in/out if provided
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(record, key, value)

    shift = db.query(Shift).filter(Shift.id == record.shift_id).first()
    if shift and record.punch_in and record.punch_out:
        result = calculate_attendance_status(
            shift_start=shift.start_time,
            shift_end=shift.end_time,
            lag_minutes=shift.lag_minutes,
            working_minutes=shift.working_minutes,
            punch_in=record.punch_in,
            punch_out=record.punch_out
        )
        record.total_worked_minutes = result["total_worked_minutes"]
        record.status = result["status"]

    db.commit()
    db.refresh(record)
    return record


# DELETE attendance
@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")
    db.delete(record)
    db.commit()
    return {"message": "Attendance deleted successfully"}
