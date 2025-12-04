# app/routes/attendance_summary_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
import calendar

from app.database import get_db
from app.models.attendance_m import Attendance
from app.models.user_m import User
from app.models.attendance_punch_m import AttendancePunch
from app.models.leavemaster_m import LeaveMaster
from app.models.permission_m import Permission
from app.models.holiday_m import Holiday

from app.schema.attendance_schema import AttendanceSummaryResponse
from app.utils.attendance_utils import calculate_monthly_summary
from app.dependencies import get_current_user

# Permission dependencies
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

ATTENDANCE_MENU_ID = 44

router = APIRouter(prefix="/attendance-summary", tags=["Attendance Summary"])


# ----------------------------------------------------
# GENERATE MONTHLY SUMMARY  (Create Permission)
# ----------------------------------------------------
@router.post(
    "/generate/{user_id}/{year}/{month}",
    response_model=AttendanceSummaryResponse,
    dependencies=[Depends(require_create_permission(ATTENDANCE_MENU_ID))]
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
# GET SUMMARY BY USER ID + YEAR + MONTH (View Permission)
# ----------------------------------------------------
@router.get(
    "/{user_id}/{year}/{month}",
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


# ----------------------------------------------------
# GET SUMMARY BY ID (View Permission)
# ----------------------------------------------------
@router.get(
    "/id/{attendance_id}",
    response_model=AttendanceSummaryResponse,
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_summary_by_id(attendance_id: int, db: Session = Depends(get_db)):

    summary = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Attendance summary not found")

    return summary


# ----------------------------------------------------
# GET ALL SUMMARIES (View Permission)
# ----------------------------------------------------
@router.get(
    "/",
    response_model=List[AttendanceSummaryResponse],
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_all_summaries(db: Session = Depends(get_db)):
    return db.query(Attendance).all()


# ----------------------------------------------------
# GET ALL SUMMARIES FOR A SPECIFIC USER (View Permission)
# ----------------------------------------------------
@router.get(
    "/user/{user_id}",
    response_model=List[AttendanceSummaryResponse],
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_summaries_for_user(user_id: int, db: Session = Depends(get_db)):

    summaries = db.query(Attendance).filter(Attendance.user_id == user_id).all()

    if not summaries:
        raise HTTPException(status_code=404, detail="No attendance summaries found")

    return summaries


# ----------------------------------------------------
# DELETE SUMMARY BY ID (Delete Permission)
# ----------------------------------------------------
@router.delete(
    "/delete/{attendance_id}",
    dependencies=[Depends(require_delete_permission(ATTENDANCE_MENU_ID))]
)
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


# ----------------------------------------------------
# ⭐ NEW FEATURE — DAILY DETAILED VIEW (View Permission)
# ----------------------------------------------------
@router.get(
    "/daily/{user_id}/{year}/{month}",
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_daily_attendance(user_id: int, year: int, month: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    month_start = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    month_end = date(year, month, days_in_month)

    # Fetch punches
    punches = db.query(AttendancePunch).filter(
        AttendancePunch.bio_id == user.biometric_id,
        AttendancePunch.punch_date >= month_start,
        AttendancePunch.punch_date <= month_end
    ).all()

    punch_map = {}
    for p in punches:
        punch_map.setdefault(p.punch_date, []).append(p)

    # Leaves
    leaves = db.query(LeaveMaster).filter(
        LeaveMaster.user_id == user_id,
        LeaveMaster.status == "approved",
        LeaveMaster.start_date <= month_end,
        (LeaveMaster.end_date == None) | (LeaveMaster.end_date >= month_start)
    ).all()

    leave_map = {}
    for l in leaves:
        d = l.start_date
        end = l.end_date or l.start_date
        while d <= end:
            leave_map[d] = l
            d += timedelta(days=1)

    # Permissions
    permissions = db.query(Permission).filter(
        Permission.user_id == user_id,
        Permission.date >= month_start,
        Permission.date <= month_end,
        Permission.status == "approved"
    ).all()

    permission_map = {p.date: p for p in permissions}

    # Holidays
    holiday_dates = {
        h.date for h in db.query(Holiday)
        .filter(Holiday.date >= month_start, Holiday.date <= month_end)
        .all()
    }

    # Sundays
    sundays = {
        month_start + timedelta(days=i)
        for i in range(days_in_month)
        if (month_start + timedelta(days=i)).weekday() == 6
    }

    # ------------------------------
    # BUILD DAYWISE RESULT
    # ------------------------------
    daywise = []

    for i in range(days_in_month):
        day = month_start + timedelta(days=i)

        punches_today = sorted(punch_map.get(day, []), key=lambda x: x.punch_time)
        punch_in = punches_today[0].punch_time if len(punches_today) >= 1 else None
        punch_out = punches_today[-1].punch_time if len(punches_today) >= 2 else None

        status = "Absent"
        worked_minutes = late = early_exit = overtime = 0
        leave_type = None
        permission_info = None

        # Holiday
        if day in holiday_dates:
            status = "Holiday"

        # Sunday
        elif day in sundays:
            status = "Sunday"

        # Leave
        elif day in leave_map:
            leave = leave_map[day]
            leave_type = leave.leave_type
            status = "Half-Day Leave" if leave.is_half_day else "Full-Day Leave"

        # Permission
        elif day in permission_map:
            p = permission_map[day]
            permission_info = {
                "from": str(p.from_time),
                "to": str(p.to_time),
                "reason": p.reason
            }
            status = "Permission"

        else:
            # Punch logic
            if punch_in and punch_out:
                in_dt = datetime.combine(day, punch_in)
                out_dt = datetime.combine(day, punch_out)

                if out_dt < in_dt:
                    out_dt += timedelta(days=1)

                worked_minutes = int((out_dt - in_dt).total_seconds() / 60)

                shift_start = datetime.combine(day, datetime.strptime("09:00", "%H:%M").time())
                shift_end = datetime.combine(day, datetime.strptime("17:00", "%H:%M").time())

                if in_dt > shift_start:
                    late = int((in_dt - shift_start).total_seconds() / 60)

                if out_dt < shift_end:
                    early_exit = int((shift_end - out_dt).total_seconds() / 60)

                if out_dt > shift_end:
                    overtime = int((out_dt - shift_end).total_seconds() / 60)

                if worked_minutes >= 480 * 0.8:
                    status = "Present"
                elif worked_minutes >= 480 * 0.5:
                    status = "Half"
                else:
                    status = "Absent"

        daywise.append({
            "date": str(day),
            "status": status,
            "punch_in": str(punch_in) if punch_in else None,
            "punch_out": str(punch_out) if punch_out else None,
            "worked_minutes": worked_minutes,
            "late_minutes": late,
            "early_exit_minutes": early_exit,
            "overtime_minutes": overtime,
            "leave_type": leave_type,
            "permission": permission_info
        })

    return {
        "user_id": user_id,
        "month": f"{year}-{month:02d}",
        "days": daywise
    }
