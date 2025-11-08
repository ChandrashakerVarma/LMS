# app/utils/attendance_utils.py
from datetime import datetime, timedelta, time


def calculate_attendance_status(
    shift_start: time,
    shift_end: time,
    lag_minutes: int,
    working_minutes: int,
    punch_in: datetime,
    punch_out: datetime,
):
    """
    Calculate attendance status based on shift timing, lag, and punch duration.
    Handles overnight shifts (e.g., 22:00–06:00 next day).
    """

    # Convert timezone-aware datetimes to naive
    if punch_in.tzinfo:
        punch_in = punch_in.replace(tzinfo=None)
    if punch_out.tzinfo:
        punch_out = punch_out.replace(tzinfo=None)

    # Determine shift start & end datetime based on punch_in date
    shift_start_dt = datetime.combine(punch_in.date(), shift_start)
    shift_end_dt = datetime.combine(punch_in.date(), shift_end)

    # Handle cross-midnight shifts
    if shift_end_dt <= shift_start_dt:
        shift_end_dt += timedelta(days=1)

    # Allow small lag buffer
    early_start = shift_start_dt - timedelta(minutes=lag_minutes)
    late_end = shift_end_dt + timedelta(minutes=lag_minutes)

    # Clip actual punches within this window
    punch_in_clipped = max(punch_in, early_start)
    punch_out_clipped = min(punch_out, late_end)

    # Ensure valid range
    if punch_out_clipped < punch_in_clipped:
        return {"total_worked_minutes": 0, "status": "Absent"}

    total_worked_minutes = int((punch_out_clipped - punch_in_clipped).total_seconds() / 60)

    # Determine status
    half_day_threshold = working_minutes // 2
    if total_worked_minutes >= working_minutes:
        status = "Full Day"
    elif total_worked_minutes >= half_day_threshold:
        status = "Half Day"
    else:
        status = "Absent"

    return {
        "total_worked_minutes": total_worked_minutes,
        "status": status
    }
