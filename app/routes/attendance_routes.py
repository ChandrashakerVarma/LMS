# app/routes/attendance_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.attendance_m import Attendance
from app.models.shift_m import Shift
from app.models.user_m import User
from app.schema.attendance_schema import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.utils.attendance_utils import calculate_attendance_status
from app.dependencies import get_current_user  # Auth Dependency


router = APIRouter(prefix="/attendance", tags=["Attendance"])


# -------------------------------
# CREATE Attendance
# -------------------------------
@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)     # ✅ FIXED
):

    # Validate shift
    shift = db.query(Shift).filter(Shift.id == payload.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    # Determine attendance date based on shift start
    attendance_date = payload.punch_in.date()

    # Prevent duplicate attendance entry
    existing = db.query(Attendance).filter(
        Attendance.user_id == payload.user_id,
        Attendance.attendance_date == attendance_date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance already exists for this user on this date"
        )

    # Validate punch timing
    if shift.start_time > shift.end_time:
        # NIGHT SHIFT
        if payload.punch_out <= payload.punch_in:
            raise HTTPException(status_code=400, detail="Night shift: punch-out must be next day")
    else:
        # DAY SHIFT
        if payload.punch_in >= payload.punch_out:
            raise HTTPException(status_code=400, detail="Punch-out must be after punch-in")

    # Calculate status and worked minutes
    result = calculate_attendance_status(
        shift_start=shift.start_time,
        shift_end=shift.end_time,
        lag_minutes=shift.lag_minutes,
        working_minutes=shift.working_minutes,
        punch_in=payload.punch_in,
        punch_out=payload.punch_out
    )

    record = Attendance(
        user_id=payload.user_id,
        shift_id=payload.shift_id,
        attendance_date=attendance_date,
        punch_in=payload.punch_in,
        punch_out=payload.punch_out,
        total_worked_minutes=result["total_worked_minutes"],
        status=result["status"],
        created_by=current_user.first_name         # ✅ FIXED
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# -------------------------------
# GET ALL Attendance
# -------------------------------
@router.get("/", response_model=List[AttendanceResponse])
def get_all_attendance(db: Session = Depends(get_db)):
    return (
        db.query(Attendance)
        .order_by(Attendance.attendance_date.desc())
        .all()
    )


# -------------------------------
# GET Attendance by ID
# -------------------------------
@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return record


# -------------------------------
# UPDATE Attendance
# -------------------------------
@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)     # ✅ FIXED
):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")

    # Update fields
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(record, key, value)

    # Validate times
    if record.punch_in and record.punch_out:
        if record.punch_in >= record.punch_out:
            raise HTTPException(status_code=400, detail="Punch-out must be after punch-in")

    # Recalculate status
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
        record.attendance_date = record.punch_in.date()

    # Track modifier
    record.modified_by = current_user.first_name       # ✅ FIXED

    db.commit()
    db.refresh(record)

    return record


# -------------------------------
# DELETE Attendance
# -------------------------------
@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)     # Optional
):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")

    db.delete(record)
    db.commit()

    return {"message": f"Attendance deleted by {current_user.first_name}"}
