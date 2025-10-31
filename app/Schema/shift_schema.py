from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ShiftBase(BaseModel):
    start_time: str
    end_time: str
    shift_code: str
    working_minutes: int
    status: Optional[str] = "Active"
    is_rotational: Optional[bool] = False

class ShiftCreate(ShiftBase):
    pass

class ShiftUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    shift_code: Optional[str] = None
    working_minutes: Optional[int] = None
    status: Optional[str] = None
    is_rotational: Optional[bool] = None

class ShiftOut(ShiftBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
