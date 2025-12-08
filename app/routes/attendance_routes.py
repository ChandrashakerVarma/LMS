from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from datetime import date, datetime, timedelta
import calendar
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

from app.models.attendance_m import Attendance
from app.models.user_m import User
from app.models.attendance_punch_m import AttendancePunch
from app.models.leavemaster_m import LeaveMaster
from app.models.permission_m import Permission
from app.models.holiday_m import Holiday

from app.schemas.attendance_schema import AttendanceResponse, AttendanceSummaryResponse
from app.utils.attendance_utils import calculate_monthly_summary


ATTENDANCE_MENU_ID = 44

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# ------------------------------------------------
# GET ALL ATTENDANCE RAW RECORDS
# ------------------------------------------------
@router.get(
    "/",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_all_attendance(db: Session = Depends(get_db)):
    return db.query(Attendance).order_by(Attendance.id.desc()).all()


# ------------------------------------------------
# GET SINGLE ATTENDANCE
# ------------------------------------------------
@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):

    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(404, "Attendance record not found")
    return record


# ------------------------------------------------
# DELETE RAW
# ------------------------------------------------
@router.delete(
    "/{attendance_id}",
    dependencies=[Depends(require_delete_permission(ATTENDANCE_MENU_ID))]
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(404, "Attendance record not found")

    db.delete(record)
    db.commit()
    return {"message": "Attendance record deleted"}


# ==========================================================
#                    MONTHLY SUMMARY SECTION
# ==========================================================

@router.post(
    "/summary/generate/{user_id}/{year}/{month}",
    response_model=AttendanceSummaryResponse,
    dependencies=[Depends(require_create_permission(ATTENDANCE_MENU_ID))]
)
def generate_summary(
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
    db.refresh(summary)
    return summary


@router.get(
    "/summary/{user_id}/{year}/{month}",
    response_model=AttendanceSummaryResponse,
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_summary(user_id: int, year: int, month: int, db: Session = Depends(get_db)):

    month_start = date(year, month, 1)
    summary = (
        db.query(Attendance)
        .filter(Attendance.user_id == user_id, Attendance.month == month_start)
        .first()
    )

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not generated")

    return summary


@router.get(
    "/summary/user/{user_id}",
    response_model=List[AttendanceSummaryResponse],
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_summaries_for_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Attendance).filter(Attendance.user_id == user_id).all()


@router.delete(
    "/summary/delete/{attendance_id}",
    dependencies=[Depends(require_delete_permission(ATTENDANCE_MENU_ID))]
)
def delete_summary(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    summary = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not summary:
        raise HTTPException(404, "Summary not found")

    db.delete(summary)
    db.commit()
    return {"message": "Summary deleted"}


# ==========================================================
#                    DAILY DETAIL VIEW
# ==========================================================
@router.get(
    "/summary/daily/{user_id}/{year}/{month}",
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_daily(user_id: int, year: int, month: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    month_start = date(year, month, 1)
    _, total_days = calendar.monthrange(year, month)
    month_end = date(year, month, total_days)

    # PUNCHES
    punches = db.query(AttendancePunch).filter(
        AttendancePunch.bio_id == user.biometric_id,
        AttendancePunch.punch_date >= month_start,
        AttendancePunch.punch_date <= month_end
    ).all()

    punch_map = {}
    for p in punches:
        punch_map.setdefault(p.punch_date, []).append(p)

    # LEAVES
    leaves = db.query(LeaveMaster).filter(
        LeaveMaster.user_id == user_id,
        LeaveMaster.status == "approved",
        LeaveMaster.start_date <= month_end,
        (LeaveMaster.end_date == None) | (LeaveMaster.end_date >= month_start)
    ).all()

    leave_map = {}
    for l in leaves:
        d = l.start_date
        until = l.end_date or l.start_date
        while d <= until:
            leave_map[d] = l
            d += timedelta(days=1)

    # HOLIDAYS
    holiday_dates = {
        h.date for h in db.query(Holiday)
        .filter(Holiday.date >= month_start, Holiday.date <= month_end)
        .all()
    }

    # SUNDAYS
    sundays = {
        month_start + timedelta(days=i)
        for i in range(total_days)
        if (month_start + timedelta(days=i)).weekday() == 6
    }

    # BUILD RESULT
    days = []
    for i in range(total_days):
        day = month_start + timedelta(days=i)

        punches_today = sorted(
            punch_map.get(day, []),
            key=lambda x: x.punch_time
        )
        punch_in = punches_today[0].punch_time if punches_today else None
        punch_out = punches_today[-1].punch_time if len(punches_today) > 1 else None

        # Default
        status = "Absent"
        worked_minutes = late = early_exit = overtime = 0

        if day in holiday_dates:
            status = "Holiday"

        elif day in sundays:
            status = "Sunday"

        elif day in leave_map:
            leave = leave_map[day]
            status = "Half-Day Leave" if leave.is_half_day else "Full-Day Leave"

        else:
            if punch_in and punch_out:
                in_dt = datetime.combine(day, punch_in)
                out_dt = datetime.combine(day, punch_out)

                if out_dt < in_dt:
                    out_dt += timedelta(days=1)

                worked_minutes = int((out_dt - in_dt).total_seconds() / 60)

                if worked_minutes >= 384:  # 8hr * 0.8
                    status = "Present"
                elif worked_minutes >= 240:  # 8hr * 0.5
                    status = "Half"
                else:
                    status = "Absent"

        days.append({
            "date": str(day),
            "status": status,
            "punch_in": str(punch_in) if punch_in else None,
            "punch_out": str(punch_out) if punch_out else None,
            "worked_minutes": worked_minutes,
        })

    return {
        "user_id": user_id,
        "month": f"{year}-{month:02d}",
        "days": days
    }
