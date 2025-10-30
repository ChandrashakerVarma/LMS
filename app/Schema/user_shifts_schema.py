from pydantic import BaseModel
from datetime import date
from typing import Optional

class UserShiftBase(BaseModel):
    user_id: int
    shift_id: int
    assigned_date: date
    is_active: Optional[bool] = True

class UserShiftCreate(UserShiftBase):
    pass

class UserShiftUpdate(BaseModel):
    shift_id: Optional[int] = None
    assigned_date: Optional[date] = None
    is_active: Optional[bool] = None

class UserShiftOut(UserShiftBase):
    id: int

    class Config:
        from_attributes = True
