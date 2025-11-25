from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base
class ShiftRosterDetailBase(BaseModel):
    shift_roster_id: int
    week_day_id: int
    shift_id: int


# Create
class ShiftRosterDetailCreate(ShiftRosterDetailBase):
    created_by: Optional[str] = None


# Update
class ShiftRosterDetailUpdate(BaseModel):
    week_day_id: Optional[int] = None
    shift_id: Optional[int] = None
    modified_by: Optional[str] = None


# Response
class ShiftRosterDetailResponse(ShiftRosterDetailBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    class Config:
        orm_mode = True
