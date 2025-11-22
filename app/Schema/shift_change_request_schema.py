from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ShiftChangeRequestBase(BaseModel):
    old_shift_id: Optional[int] = None
    new_shift_id: int
    request_date: date
    reason: Optional[str] = None
    status: Optional[str] = "Pending"


class ShiftChangeRequestCreate(ShiftChangeRequestBase):
    pass


class ShiftChangeRequestUpdate(BaseModel):
    status: Optional[str] = None
    reason: Optional[str] = None


class ShiftChangeRequestOut(ShiftChangeRequestBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    modified_by: str | None = None

    class Config:
        from_attributes = True
