from pydantic import BaseModel
from typing import Optional

class LeaveBase(BaseModel):
    leave_type: str
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[int] # Input/output format: dd-mm-yyyy
    allocated: Optional[int] = 0
    used: Optional[int] = 0
    balance: Optional[int] = 0
    carry_forward: Optional[bool] = False
    user_id: Optional[int] = None

class LeaveCreate(LeaveBase):
    pass

class LeaveOut(LeaveBase):
    id: int

    class Config:
        from_attributes = True
