from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


# -------------------- BASE --------------------
class CandidateBase(BaseModel):
    job_posting_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    applied_date: date
    resume_url: Optional[str] = None


# -------------------- CREATE --------------------
class CandidateCreate(CandidateBase):
    pass


# -------------------- UPDATE --------------------
class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    applied_date: Optional[date] = None
    resume_url: Optional[str] = None
    status: Optional[str] = None   # Pending / Approved / Rejected


# -------------------- OUTPUT --------------------
class CandidateOut(CandidateBase):
    id: int
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    modified_by: str | None = None

    class Config:
        orm_mode = True
