from pydantic import BaseModel
from typing import Optional
from datetime import date


class ShiftChangeRequestBase(BaseModel):
    user_id: int
    old_shift_id: Optional[int] = None
    new_shift_id: int
    request_date: date
    reason: Optional[str] = None
    status: Optional[str] = "Pending"


class ShiftChangeRequestCreate(ShiftChangeRequestBase):
    pass


class ShiftChangeRequestUpdate(BaseModel):
    status: Optional[str] = None
    reason: Optional[str] = None


class ShiftChangeRequestOut(ShiftChangeRequestBase):
    id: int

    class Config:
        from_attributes = True
