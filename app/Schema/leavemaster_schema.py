from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class LeaveMasterBase(BaseModel):
    holiday: str
    description: Optional[str] = None
    user_id: int
    allocated: Optional[int] = 0
    used: Optional[int] = 0
    balance: Optional[int] = 0
    carry_forward: Optional[bool] = False
    leave_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class LeaveMasterCreate(LeaveMasterBase):
    pass


class LeaveMasterUpdate(BaseModel):
    holiday: Optional[str] = None
    description: Optional[str] = None
    allocated: Optional[int] = None
    used: Optional[int] = None
    balance: Optional[int] = None
    carry_forward: Optional[bool] = None
    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class LeaveMasterOut(LeaveMasterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
