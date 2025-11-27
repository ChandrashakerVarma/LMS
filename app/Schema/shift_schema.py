from pydantic import BaseModel
from datetime import time
from typing import Optional

class ShiftBase(BaseModel):
    shift_name: str
    shift_code: str
    shift_type: Optional[str] = None
    start_time: time
    end_time: time
    working_minutes: int
    lag_minutes: Optional[int] = 60
    description: Optional[str] = None
    status: Optional[str] = "active"

    # ✔ added field
    is_week_off: Optional[int] = 0


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    shift_name: Optional[str] = None
    shift_code: Optional[str] = None
    shift_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    working_minutes: Optional[int] = None
    lag_minutes: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None

    # ✔ added
    is_week_off: Optional[int] = None


class ShiftResponse(ShiftBase):
    id: int
    created_by: int

    class Config:
        orm_mode = True
