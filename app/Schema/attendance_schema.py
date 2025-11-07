# app/schema/attendance_schema.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class AttendanceBase(BaseModel):
    user_id: int
    shift_id: int
    punch_in: datetime
    punch_out: datetime


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    punch_in: Optional[datetime] = None
    punch_out: Optional[datetime] = None
    status: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    id: int
    attendance_date: date
    total_worked_minutes: Optional[int]
    status: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
