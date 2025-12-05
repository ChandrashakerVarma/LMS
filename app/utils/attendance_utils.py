# D:\LMS\app\utils\attendance_utils.py

from datetime import datetime, timedelta, time
from typing import Tuple, Optional

from app.models.attendance_location_policy_m import AttendanceLocationPolicy
from app.models.user_m import User
from app.utils.geo_utils import haversine_distance as external_haversine  # optional if you already have geo_utils
from app.database import SessionLocal

# ------------------------------
# Attendance time calculations
# ------------------------------
def calculate_attendance_status(
    shift_start: time,
    shift_end: time,
    lag_minutes: int,
    working_minutes: int,
    check_in_time: datetime,
    punch_out: datetime,
) -> dict:
    """
    Calculate the attendance status and total worked minutes.
    Handles cross-midnight shifts.
    Returns: {"total_worked_minutes": int, "status": "Full Day"|"Half Day"|"Absent"}
    """

    # normalize tz-aware datetimes to naive (UTC)
    if check_in_time.tzinfo:
        check_in_time = check_in_time.replace(tzinfo=None)
    if punch_out.tzinfo:
        punch_out = punch_out.replace(tzinfo=None)

    # Build shift start/end datetimes on check_in_time date
    shift_start_dt = datetime.combine(check_in_time.date(), shift_start)
    shift_end_dt = datetime.combine(check_in_time.date(), shift_end)

    # If shift_end is earlier or equal to start → next day
    if shift_end_dt <= shift_start_dt:
        shift_end_dt = shift_end_dt + timedelta(days=1)

    # Allow small lag buffer both sides
    earliest_allowed = shift_start_dt - timedelta(minutes=lag_minutes)
    latest_allowed = shift_end_dt + timedelta(minutes=lag_minutes)

    # Clip punches to window
    check_in_clipped = max(check_in_time, earliest_allowed)
    punch_out_clipped = min(punch_out, latest_allowed)

    if punch_out_clipped < check_in_clipped:
        return {"total_worked_minutes": 0, "status": "Absent"}

    total_worked_minutes = int((punch_out_clipped - check_in_clipped).total_seconds() / 60)

    half_day_threshold = working_minutes // 2
    if total_worked_minutes >= working_minutes:
        status = "Full Day"
    elif total_worked_minutes >= half_day_threshold:
        status = "Half Day"
    else:
        status = "Absent"

    return {"total_worked_minutes": total_worked_minutes, "status": status}


# ------------------------------
# Haversine distance (meters)
# ------------------------------
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute distance in meters between two lat/long points using Haversine formula.
    If you already have app.utils.geo_utils.haversine_distance, you can use that instead.
    """
    try:
        # Prefer external helper if available (keeps behaviour consistent)
        if external_haversine:
            return external_haversine(lat1, lon1, lat2, lon2)
    except Exception:
        # fallthrough to internal implementation
        pass

    from math import radians, sin, cos, asin, sqrt

    R = 6371000.0  # Earth radius in meters

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2.0) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2.0) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


# ------------------------------
# Resolve active policy (User > Branch > Organization)
# ------------------------------
def resolve_location_policy(db, user_id: int, branch_id: Optional[int] = None, organization_id: Optional[int] = None) -> Optional[AttendanceLocationPolicy]:
    """
    Return the most-specific active AttendanceLocationPolicy.
    Priority: User -> Branch -> Organization
    """
    # 1) user policy
    policy = (
        db.query(AttendanceLocationPolicy)
        .filter(AttendanceLocationPolicy.user_id == user_id, AttendanceLocationPolicy.is_active.is_(True))
        .first()
    )

    if policy:
        return policy

    # 2) branch policy
    if branch_id:
        policy = (
            db.query(AttendanceLocationPolicy)
            .filter(AttendanceLocationPolicy.branch_id == branch_id, AttendanceLocationPolicy.is_active.is_(True))
            .first()
        )
        if policy:
            return policy

    # 3) organization policy
    if organization_id:
        policy = (
            db.query(AttendanceLocationPolicy)
            .filter(AttendanceLocationPolicy.organization_id == organization_id, AttendanceLocationPolicy.is_active.is_(True))
            .first()
        )
        if policy:
            return policy

    return None


# ------------------------------
# Check location against policy
# ------------------------------
def check_location(db, user_id: int, branch_id: Optional[int], organization_id: Optional[int], lat: Optional[float], long: Optional[float]) -> Tuple[str, bool]:
    """
    Evaluate lat/long against resolved policy.
    Returns (status_string, allowed_bool)

    status_string: one of "INSIDE", "OUTSIDE", "WFA", "ANY"
    """

    policy = resolve_location_policy(db, user_id, branch_id, organization_id)

    # No policy configured -> allow by default (INSIDE)
    if not policy:
        return "INSIDE", True

    # Work from anywhere mode on policy
    if policy.mode == "WFA":
        return "WFA", True

    # Anywhere allowed
    if policy.mode == "ANYWHERE":
        return "ANY", True

    # GEO_FENCE mode requires allowed_lat/long
    if policy.mode == "GEO_FENCE":
        if lat is None or long is None:
            # Missing coords → treat as outside
            return "OUTSIDE", False

        if policy.allowed_lat is None or policy.allowed_long is None:
            return "OUTSIDE", False

        radius = policy.radius_meters or 200  # default 200m if not set
        distance = haversine_distance(lat, long, policy.allowed_lat, policy.allowed_long)

        if distance <= radius:
            return "INSIDE", True
        else:
            return "OUTSIDE", False

    # Default fallback: allow
    return "INSIDE", True


# ------------------------------
# Helper: get user attendance_mode (WFH/BRANCH/ANY)
# ------------------------------
def get_user_attendance_mode(db, user_id: int) -> str:
    """
    Read `attendance_mode` from user row. Returns uppercase string:
    "BRANCH" (default), "WFH", or "ANY".
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return "BRANCH"
    mode = (user.attendance_mode or "BRANCH").upper()
    if mode == "WFH":
        return "WFH"
    if mode == "ANY":
        return "ANY"
    return "BRANCH"
