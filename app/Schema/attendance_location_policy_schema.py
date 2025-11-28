from typing import Optional
from pydantic import BaseModel


class AttendanceLocationPolicyBase(BaseModel):
    mode: str
    allowed_lat: Optional[float] = None
    allowed_long: Optional[float] = None
    radius_meters: Optional[int] = 200
    user_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None


class AttendanceLocationPolicyRead(AttendanceLocationPolicyBase):
    id: int

    class Config:
        from_attributes = True
