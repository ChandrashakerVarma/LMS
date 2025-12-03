# app/routes/attendance_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.attendance_m import Attendance
from app.schema.attendance_schema import AttendanceSummaryResponse
from app.utils.attendance_utils import calculate_monthly_summary
from app.dependencies import get_current_user

router = APIRouter(prefix="/attendance", tags=["Attendance Summary"])


# ----------------------------------------------------
# GENERATE MONTHLY SUMMARY
# ----------------------------------------------------
@router.post(
    "/generate/{user_id}/{year}/{month}",
    response_model=AttendanceSummaryResponse
)
def generate_monthly_summary(
    user_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    summary = calculate_monthly_summary(db, user_id, year, month)

    if not summary:
        raise HTTPException(status_code=404, detail="User not found")

    summary.created_by = current_user.first_name
    db.commit()

    return summary


# ----------------------------------------------------
# GET SUMMARY BY USER ID + YEAR + MONTH
# ----------------------------------------------------
@router.get(
    "/{user_id}/{year}/{month}",
    response_model=AttendanceSummaryResponse
)
def get_summary(
    user_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    month_start = date(year, month, 1)

    summary = (
        db.query(Attendance)
        .filter(Attendance.user_id == user_id, Attendance.month == month_start)
        .first()
    )

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not generated")

    return summary


# ----------------------------------------------------
# GET SUMMARY BY ATTENDANCE ID
# ----------------------------------------------------
@router.get(
    "/id/{attendance_id}",
    response_model=AttendanceSummaryResponse
)
def get_summary_by_id(attendance_id: int, db: Session = Depends(get_db)):

    summary = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Attendance summary not found")

    return summary


# ----------------------------------------------------
# GET ALL SUMMARIES
# ----------------------------------------------------
@router.get("/", response_model=List[AttendanceSummaryResponse])
def get_all_summaries(db: Session = Depends(get_db)):
    return db.query(Attendance).all()


# ----------------------------------------------------
# GET ALL SUMMARIES FOR A SPECIFIC USER
# ----------------------------------------------------
@router.get(
    "/user/{user_id}",
    response_model=List[AttendanceSummaryResponse]
)
def get_summaries_for_user(user_id: int, db: Session = Depends(get_db)):

    summaries = db.query(Attendance).filter(Attendance.user_id == user_id).all()

    if not summaries:
        raise HTTPException(status_code=404, detail="No attendance summaries found")

    return summaries


# ----------------------------------------------------
# DELETE SUMMARY BY ID
# ----------------------------------------------------
@router.delete("/delete/{attendance_id}")
def delete_summary(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    summary = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Attendance summary not found")

    db.delete(summary)
    db.commit()

    return {
        "message": f"Attendance summary deleted successfully by {current_user.first_name}"
    }
