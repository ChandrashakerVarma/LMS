from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time


class ShiftBase(BaseModel):
    shift_name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    shift_code: Optional[str] = None
    shift_type: Optional[str] = None  # Day / Night etc.
    working_minutes: Optional[int] = None
    lag_minutes: Optional[int] = 60
    status: Optional[str] = "active"


class ShiftCreate(BaseModel):
    shift_name: str
    description: Optional[str] = None
    start_time: time
    end_time: time
    shift_code: str
    shift_type: Optional[str] = None
    working_minutes: int
    lag_minutes: Optional[int] = 60
    status: Optional[str] = "active"


class ShiftUpdate(ShiftBase):
    pass


class ShiftOut(ShiftBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
