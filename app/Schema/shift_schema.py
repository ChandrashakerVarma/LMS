from pydantic import BaseModel
from datetime import time, datetime
from typing import Optional


# Base schema (shared fields)
class ShiftBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    description: Optional[str] = None
    shift_code: str
    shift_name: str
    working_minutes: int
    status: Optional[str] = "active"


# For creating a new shift
class ShiftCreate(ShiftBase):
    pass


# For updating an existing shift
class ShiftUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    shift_code: Optional[str] = None
    shift_name: Optional[str] = None
    working_minutes: Optional[int] = None
    status: Optional[str] = None


# Response schema
class ShiftResponse(ShiftBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes  = True
