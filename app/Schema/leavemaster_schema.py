# app/schema/leave_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# Base Schema
class LeaveMasterBase(BaseModel):
    # holiday: Optional[bool] = False   # False = Leave balance, True = Holiday
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = True
    date: Optional[date] = None # type: ignore
    user_id: Optional[int] = None
    year: Optional[int] = None
    allocated: Optional[int] = 0
    used: Optional[int] = 0
    balance: Optional[int] = 0
    carry_forward: Optional[bool] = False


# Create Schema
class LeaveMasterCreate(LeaveMasterBase):
    pass


# Update Schema
class LeaveMasterUpdate(LeaveMasterBase):
    pass


# Response Schema
class LeaveMasterResponse(LeaveMasterBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
