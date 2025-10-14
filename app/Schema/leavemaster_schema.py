from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# ---------------------- Base Schema ----------------------
class LeaveMasterBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = True
    leave_date: Optional[date] = None  # Must match model
    user_id: Optional[int] = None
    year: Optional[int] = None
    allocated: Optional[int] = 0
    used: Optional[int] = 0
    balance: Optional[int] = 0
    carry_forward: Optional[bool] = False
    holiday: Optional[bool] = False

# ---------------------- Create Schema ----------------------
class LeaveMasterCreate(LeaveMasterBase):
    pass

# ---------------------- Update Schema ----------------------
class LeaveMasterUpdate(LeaveMasterBase):
    pass

# ---------------------- Response Schema ----------------------
class LeaveMasterResponse(LeaveMasterBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
