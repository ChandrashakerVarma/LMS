from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    shift_id: Optional[int] = None

    # AI Attendance fields
    check_in_time: Optional[datetime] = None
    punch_out: Optional[datetime] = None

    check_in_lat: Optional[float] = None
    check_in_long: Optional[float] = None

    gps_score: Optional[float] = None
    location_status: Optional[str] = None

    is_face_verified: Optional[int] = None
    face_confidence: Optional[float] = None

    total_worked_minutes: Optional[int] = None
    status: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
