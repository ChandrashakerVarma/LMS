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
    Supports overnight shifts (e.g., 10 PM to 6 AM next day).
    """

    # Convert timezone-aware datetimes to naive
    if punch_in.tzinfo:
        punch_in = punch_in.replace(tzinfo=None)
    if punch_out.tzinfo:
        punch_out = punch_out.replace(tzinfo=None)

    # Determine shift start & end datetime based on punch_in date
    shift_start_dt = datetime.combine(punch_in.date(), shift_start)
    shift_end_dt = datetime.combine(punch_in.date(), shift_end)

    # Handle overnight shifts
    if shift_end_dt <= shift_start_dt:
        shift_end_dt += timedelta(days=1)

    # Lag window
    early_start = shift_start_dt - timedelta(minutes=lag_minutes)
    late_end = shift_end_dt + timedelta(minutes=lag_minutes)

    # Clip punch_in/out to valid window
    punch_in_clipped = max(punch_in, early_start)
    punch_out_clipped = min(punch_out, late_end)

    # Total worked minutes
    total_worked_minutes = int((punch_out_clipped - punch_in_clipped).total_seconds() / 60)

    # Attendance rules
    half_day_threshold = working_minutes // 2
    quarter_day_threshold = half_day_threshold // 2

    if total_worked_minutes >= half_day_threshold:
        status = "Full Day"
    elif quarter_day_threshold <= total_worked_minutes < half_day_threshold:
        status = "Half Day"
    else:
        status = "Absent"

    return {
        "total_worked_minutes": total_worked_minutes,
        "status": status
    }
