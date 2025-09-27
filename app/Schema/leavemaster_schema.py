# app/schema/leavemaster_schema.py
from pydantic import BaseModel
from typing import Optional, Union
from datetime import date, datetime


# -------- Common Base --------
class LeaveMasterCommon(BaseModel):
    id: Optional[int] = None
    holiday: bool
    name: Optional[str] = None
    description: Optional[str] = None
    status: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# -------- Holiday Schema --------
class LeaveMasterCreateHoliday(LeaveMasterCommon):
    holiday: bool = True
    date: date


# -------- Leave Balance Schema --------
class LeaveMasterCreateBalance(LeaveMasterCommon):
    holiday: bool = False
    user_id: int
    year: int
    allocated: int = 0
    used: int = 0
    balance: int = 0
    carry_forward: bool = False


# -------- Update Schemas --------
class LeaveMasterUpdateHoliday(LeaveMasterCreateHoliday):
    id: Optional[int] = None
    date: Optional[date] = None # type: ignore

class LeaveMasterUpdateBalance(LeaveMasterCreateBalance):
    id: Optional[int] = None
    user_id: Optional[int] = None
    year: Optional[int] = None


# -------- Response (Union) --------
LeaveMasterResponse = Union[LeaveMasterCreateHoliday, LeaveMasterCreateBalance]
