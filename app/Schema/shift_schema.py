from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time


# ----------------------- BASE -----------------------
class ShiftBase(BaseModel):
    shift_name: Optional[str] = None
    shift_code: Optional[str] = None
    shift_type: Optional[str] = None        # Day / Night etc.
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    working_minutes: Optional[int] = None
    lag_minutes: Optional[int] = 60
    description: Optional[str] = None
    status: Optional[str] = "active"

    # NEW FIELD
    is_week_off: Optional[int] = 0


# ----------------------- CREATE -----------------------
class ShiftCreate(BaseModel):
    shift_name: str
    shift_code: str
    shift_type: Optional[str] = None
    start_time: time
    end_time: time
    working_minutes: int
    lag_minutes: Optional[int] = 60
    description: Optional[str] = None
    status: Optional[str] = "active"

    # NEW FIELD
    is_week_off: Optional[int] = 0

    # Audit user tracking
    created_by: Optional[str] = None


# ----------------------- UPDATE -----------------------
class ShiftUpdate(ShiftBase):
    # Audit tracking
    modified_by: Optional[str] = None
    pass


# ----------------------- RESPONSE -----------------------
class ShiftOut(ShiftBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    class Config:
        orm_mode = True
