from pydantic import BaseModel
from typing import Optional
<<<<<<< HEAD

class LeaveBase(BaseModel):
    leave_type: str
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[int] # Input/output format: dd-mm-yyyy
=======
from datetime import date, datetime

# ---------------------- Base Schema ----------------------
class LeaveMasterBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = True
    leave_date: Optional[date] = None  # Must match model
    user_id: Optional[int] = None
    year: Optional[int] = None
>>>>>>> origin/main
    allocated: Optional[int] = 0
    used: Optional[int] = 0
    balance: Optional[int] = 0
    carry_forward: Optional[bool] = False
<<<<<<< HEAD
    user_id: Optional[int] = None

class LeaveCreate(LeaveBase):
    pass

class LeaveOut(LeaveBase):
    id: int

    class Config:
        from_attributes = True
=======
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
>>>>>>> origin/main
