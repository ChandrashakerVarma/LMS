# app/schema/permission_schema.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class PermissionBase(BaseModel):
    date: date
    reason: Optional[str] = None

class PermissionCreate(PermissionBase):
    user_id: int
    shift_id: int   # Manager must assign based on a shift

class PermissionUpdate(BaseModel):
    status: Optional[str] = None   # pending / approved / cancelled
    reason: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int
    user_id: int
    shift_id: int
    status: str

    class Config:
        orm_mode = True
