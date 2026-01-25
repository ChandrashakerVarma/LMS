from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date as DateType, time as TimeType
from typing import Optional, Literal


# ----------- Base Schema -----------  
class AttendancePunchBase(BaseModel):
    bio_id: str
    punch_date: DateType
    punch_time: TimeType
    punch_type: Literal["IN", "OUT"] = Field(...)  # ✅ REQUIRED & VALIDATED


# ----------- Create Schema -----------  
class AttendancePunchCreate(AttendancePunchBase):
    pass


# ----------- Update Schema -----------  
class AttendancePunchUpdate(BaseModel):
    punch_date: Optional[DateType] = None
    punch_time: Optional[TimeType] = None
    punch_type: Optional[Literal["IN", "OUT"]] = None


# ----------- Response Schema -----------  
class AttendancePunchResponse(BaseModel):
    id: int
    bio_id: str
    punch_date: DateType
    punch_time: TimeType
    punch_type: str

    created_by: Optional[str]
    modified_by: Optional[str]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
