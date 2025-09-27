from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class LeaveMasterBase(BaseModel):
    holiday: Optional[bool] = True
    name: Optional[str]
    description: Optional[str]
    status: Optional[bool] = True
    date: Optional[date]
    user_id: Optional[int]
    year: Optional[int]
    allocated: Optional[int] = 0
    used: Optional[int] = 0
    balance: Optional[int] = 0
    carry_forward: Optional[bool] = False

class LeaveMasterCreate(LeaveMasterBase):
    pass

class LeaveMasterUpdate(LeaveMasterBase):
    pass

class LeaveMasterResponse(LeaveMasterBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
