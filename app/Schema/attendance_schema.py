from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttendanceBase(BaseModel):
    user_id: int
    punch_id: str
    first_punch: Optional[datetime] = None
    last_punch: Optional[datetime] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    first_punch: Optional[datetime] = None
    last_punch: Optional[datetime] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None


class AttendanceOut(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
