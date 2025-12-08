
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional


# -----------------------------------------
# 🟡 existing model stays untouched
# -----------------------------------------
class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    shift_id: int | None = None
    check_in_time: datetime | None = None
    punch_out: datetime | None = None
    check_in_lat: float | None = None
    check_in_long: float | None = None
    gps_score: float | None = None
    location_status: str | None = None
    is_face_verified: int | None = None
    face_confidence: float | None = None
    total_worked_minutes: int | None = None
    status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# -----------------------------------------
# 🆕 MONTHLY SUMMARY RESPONSE
# -----------------------------------------
class AttendanceSummaryResponse(BaseModel):
    id: int
    user_id: int
    month: date

    present_days: int | None = None
    absent_days: int | None = None
    half_days: int | None = None
    total_working_days: int | None = None

    leave_days: int | None = None
    working_hours: float | None = None

    created_by: str | None = None

    class Config:
        from_attributes = True
