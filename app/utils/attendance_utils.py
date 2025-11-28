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
# ------------------------------
# AI FACE + GEO LOCATION POLICY
# ------------------------------

from app.models.attendance_location_policy_m import AttendanceLocationPolicy
from app.utils.geo_utils import haversine_distance


def resolve_location_policy(db, user_id, branch_id=None, organization_id=None):
    """
    Priority order: User > Branch > Organization
    """
    # User-specific policy
    policy = (
        db.query(AttendanceLocationPolicy)
        .filter(
            AttendanceLocationPolicy.user_id == user_id,
            AttendanceLocationPolicy.is_active.is_(True),
        )
        .first()
    )

    # Branch policy
    if not policy and branch_id:
        policy = (
            db.query(AttendanceLocationPolicy)
            .filter(
                AttendanceLocationPolicy.branch_id == branch_id,
                AttendanceLocationPolicy.is_active.is_(True),
            )
            .first()
        )

    # Organization policy
    if not policy and organization_id:
        policy = (
            db.query(AttendanceLocationPolicy)
            .filter(
                AttendanceLocationPolicy.organization_id == organization_id,
                AttendanceLocationPolicy.is_active.is_(True),
            )
            .first()
        )

    return policy


def check_location(db, user_id, branch_id, organization_id, lat, long):
    """
    Returns:
        ("INSIDE", True)
        ("OUTSIDE", False)
        ("WFA", True)
    """

    policy = resolve_location_policy(db, user_id, branch_id, organization_id)

    # If no policy → allow attendance normally
    if not policy:
        return "INSIDE", True

    # Work From Anywhere
    if policy.mode == "WFA":
        return "WFA", True

    # No restriction
    if policy.mode == "ANYWHERE":
        return "INSIDE", True

    # Geo-fencing mode
    if policy.mode == "GEO_FENCE":
        if policy.allowed_lat is None or policy.allowed_long is None:
            return "OUTSIDE", False

        distance = haversine_distance(lat, long, policy.allowed_lat, policy.allowed_long)

        if distance <= (policy.radius_meters or 200):
            return "INSIDE", True
        else:
            return "OUTSIDE", False

    return "INSIDE", True
