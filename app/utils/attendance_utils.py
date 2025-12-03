# app/utils/attendance_util.py

import calendar
from datetime import date, datetime, timedelta, time
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.attendance_punch_m import AttendancePunch
from app.models.holiday_m import Holiday
from app.models.leavemaster_m import LeaveMaster
from app.models.permission_m import Permission
from app.models.user_m import User
from app.models.shift_m import Shift
from app.models.shift_roster_detail_m import ShiftRosterDetail
from app.models.attendance_m import Attendance


DEFAULT_WORKING_MINUTES = 480
DEFAULT_LAG_MINUTES = 0


# -------------------------------------------
# Helpers
# -------------------------------------------
def daterange(start: date, end: date):
    while start <= end:
        yield start
        start += timedelta(days=1)


def expand_leave_dates(leave_records: List[LeaveMaster]):
    """Return date → is_half_day (True/False/None)"""
    leave_map = {}
    for rec in leave_records:
        is_half = rec.is_half_day  # True = half-day leave

        if rec.start_date and rec.end_date:
            for d in daterange(rec.start_date, rec.end_date):
                leave_map[d] = is_half
        elif rec.start_date:
            leave_map[rec.start_date] = is_half
    return leave_map


# ---------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------
def calculate_monthly_summary(db: Session, user_id: int, year: int, month: int):

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.biometric_id:
        return None

    # Month range
    month_start = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    month_end = date(year, month, days_in_month)

    # Punches
    punches = db.query(AttendancePunch).filter(
        AttendancePunch.bio_id == user.biometric_id,
        AttendancePunch.punch_date >= month_start,
        AttendancePunch.punch_date <= month_end
    ).all()

    punch_map: Dict[date, List[AttendancePunch]] = {}
    for p in punches:
        punch_map.setdefault(p.punch_date, []).append(p)

    # Holidays
    holiday_dates = {
        h.date
        for h in db.query(Holiday)
        .filter(Holiday.date >= month_start, Holiday.date <= month_end)
        .all()
    }

    # Sundays
    sundays = {
        month_start + timedelta(days=i)
        for i in range(days_in_month)
        if (month_start + timedelta(days=i)).weekday() == 6
    }

    # Leaves
    approved_leaves = db.query(LeaveMaster).filter(
        LeaveMaster.user_id == user_id,
        LeaveMaster.status == "approved",
        LeaveMaster.start_date <= month_end,
        or_(
            LeaveMaster.end_date == None,
            LeaveMaster.end_date >= month_start
        )
    ).all()

    leave_map = expand_leave_dates(approved_leaves)

    # Permissions
    permission_records = db.query(Permission).filter(
        Permission.user_id == user_id,
        Permission.date >= month_start,
        Permission.date <= month_end,
        Permission.status == "approved"
    ).all()

    permission_map = {p.date: p for p in permission_records}

    # Roster
    weekly_map = {}
    if user.shift_roster_id:
        details = db.query(ShiftRosterDetail).filter(
            ShiftRosterDetail.shift_roster_id == user.shift_roster_id
        ).all()
        weekly_map = {d.week_day_id: d.shift_id for d in details}

    shifts = {}
    if weekly_map:
        shift_objs = db.query(Shift).filter(
            Shift.id.in_(weekly_map.values())
        ).all()
        shifts = {s.id: s for s in shift_objs}

    # Counters
    present = half = absent = 0
    leaves_full = 0
    permissions = 0

    total_work = overtime = late = early_exit = 0

    # -------------------------------------------
    # DAILY LOOP
    # -------------------------------------------
    for i in range(days_in_month):
        day = month_start + timedelta(days=i)

        # --------------------------------------------------------
        # FULL-DAY LEAVE
        # --------------------------------------------------------
        if day in leave_map and (leave_map[day] is False or leave_map[day] is None):
            leaves_full += 1
            continue

        # --------------------------------------------------------
        # HALF-DAY LEAVE
        # --------------------------------------------------------
        if day in leave_map and leave_map[day] is True:

            if day not in punch_map or len(punch_map[day]) < 2:
                absent += 1
                continue

            half += 1  # count in half_days only

            # Work minutes for the half-day
            punches_today = sorted(punch_map[day], key=lambda x: x.punch_time)
            in_dt = datetime.combine(day, punches_today[0].punch_time)
            out_dt = datetime.combine(day, punches_today[-1].punch_time)
            if out_dt < in_dt:
                out_dt += timedelta(days=1)

            total_work += int((out_dt - in_dt).total_seconds() / 60)
            continue

        # --------------------------------------------------------
        # Sundays / Holidays
        # --------------------------------------------------------
        if day in holiday_dates or day in sundays:
            continue

        # --------------------------------------------------------
        # Permissions (do NOT skip — calculate!)
        # --------------------------------------------------------
        permission_obj = permission_map.get(day)
        has_permission = permission_obj is not None
        if has_permission:
            permissions += 1

        # --------------------------------------------------------
        # ABSENT: No punches
        # --------------------------------------------------------
        if day not in punch_map:
            absent += 1
            continue

        punches_today = sorted(punch_map[day], key=lambda x: x.punch_time)

        # ABSENT: only 1 punch
        if len(punches_today) < 2:
            absent += 1
            continue

        # --------------------------------------------------------
        # REGULAR WORK CALC
        # --------------------------------------------------------
        first = punches_today[0]
        lastp = punches_today[-1]

        in_dt = datetime.combine(day, first.punch_time)
        out_dt = datetime.combine(day, lastp.punch_time)
        if out_dt < in_dt:
            out_dt += timedelta(days=1)

        # Shift
        shift_obj = shifts.get(weekly_map.get(day.isoweekday()))
        working_minutes = getattr(shift_obj, "working_minutes", DEFAULT_WORKING_MINUTES)
        lag = getattr(shift_obj, "lag_minutes", DEFAULT_LAG_MINUTES)

        s_start = getattr(shift_obj, "start_time", time(9, 0))
        s_end = getattr(shift_obj, "end_time", time(17, 0))

        start_dt = datetime.combine(day, s_start)
        end_dt = datetime.combine(day, s_end)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        # LATE (uses grace)
        allowed_in = start_dt + timedelta(minutes=lag)

        # EARLY EXIT (NO grace)
        allowed_out = end_dt

        # Work minutes
        worked = int((out_dt - in_dt).total_seconds() / 60)
        total_work += worked

        # -------------------------
        # Late Entry Logic
        # -------------------------
        if has_permission:
            perm_start = datetime.combine(day, permission_obj.from_time)
            # ignore late if in permission window
            if not (allowed_in <= in_dt <= perm_start):
                if in_dt > allowed_in:
                    late += int((in_dt - allowed_in).total_seconds() / 60)
        else:
            if in_dt > allowed_in:
                late += int((in_dt - allowed_in).total_seconds() / 60)

        # -------------------------
        # Early Exit Logic
        # -------------------------
        if has_permission:
            perm_end = datetime.combine(day, permission_obj.to_time)
            # ignore early exit inside permission period
            if not (perm_end <= out_dt <= end_dt):
                if out_dt < end_dt:
                    early_exit += int((end_dt - out_dt).total_seconds() / 60)
        else:
            if out_dt < end_dt:
                early_exit += int((end_dt - out_dt).total_seconds() / 60)

        # -------------------------
        # Overtime
        # -------------------------
        if out_dt > end_dt:
            overtime += int((out_dt - end_dt).total_seconds() / 60)

        # -------------------------
        # Classification (present/half/absent)
        # -------------------------
        if worked >= working_minutes * 0.80:
            present += 1
        elif worked >= working_minutes * 0.50:
            half += 1
        else:
            absent += 1

    # -------------------------------------------------------
    # SAVE SUMMARY
    # -------------------------------------------------------
    summary = db.query(Attendance).filter(
        Attendance.user_id == user_id,
        Attendance.month == month_start
    ).first()

    if not summary:
        summary = Attendance(
            user_id=user_id,
            month=month_start,
            created_by="system"
        )
        db.add(summary)

    summary.total_days = days_in_month
    summary.present_days = present
    summary.half_days = half
    summary.absent_days = absent
    summary.holidays = len(holiday_dates)
    summary.sundays = len(sundays)
    summary.leaves = leaves_full
    summary.permissions = permissions

    summary.total_work_minutes = total_work
    summary.overtime_minutes = overtime
    summary.late_minutes = late
    summary.early_exit_minutes = early_exit

    if absent == 0 and late == 0:
        summary.summary_status = "Perfect"
    elif absent <= 2:
        summary.summary_status = "Good"
    else:
        summary.summary_status = "Poor"

    db.commit()
    db.refresh(summary)
    return summary
