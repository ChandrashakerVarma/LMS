from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---------------------- BASE ----------------------
class ShiftRosterBase(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = True


# ---------------------- CREATE ----------------------
class ShiftRosterCreate(BaseModel):
    name: str
    is_active: Optional[bool] = True

    # Audit field
    created_by: Optional[str] = None


# ---------------------- UPDATE ----------------------
class ShiftRosterUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

    # Audit field
    modified_by: Optional[str] = None


# ---------------------- RESPONSE ----------------------
class ShiftRosterResponse(ShiftRosterBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    class Config:
        orm_mode = True
