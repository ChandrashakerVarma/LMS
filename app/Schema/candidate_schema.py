from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class CandidateBase(BaseModel):
    workflow_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    applied_date: date
    resume_url: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    applied_date: Optional[date] = None
    resume_url: Optional[str] = None


class CandidateOut(CandidateBase):
    id: int

    class Config:
        from_attributes = True
