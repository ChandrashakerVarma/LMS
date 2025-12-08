from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str

class CandidateCreate(CandidateBase):
    job_posting_id: int
    resume_url: Optional[str] = None

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    resume_url: Optional[str] = None
    status: Optional[str] = None

class CandidateResponse(BaseModel):
    id: int
    job_posting_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    applied_date: date
    resume_url: Optional[str]
    status: Optional[str]

    model_config = {"from_attributes": True}
