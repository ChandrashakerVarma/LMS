# app/schema/leave_schema.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

# -------- BASE --------
class LeaveMasterBase(BaseModel):
    allocated: int = 0
    used: int = 0
    balance: int = 0
    carry_forward: bool = False

    leave_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "pending"

    # HALF DAY SUPPORT
    is_half_day: Optional[bool] = None   # None => not a half-day leave


# -------- CREATE --------
class LeaveMasterCreate(LeaveMasterBase):
    user_id: int


# -------- UPDATE --------
class LeaveMasterUpdate(BaseModel):
    allocated: Optional[int] = None
    used: Optional[int] = None
    balance: Optional[int] = None
    carry_forward: Optional[bool] = None

    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

    is_half_day: Optional[bool] = None  # update half-day if needed


# -------- RESPONSE --------
class LeaveMasterResponse(LeaveMasterBase):
    id: int
    user_id: int

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
