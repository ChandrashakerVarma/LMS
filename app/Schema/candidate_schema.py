from pydantic import BaseModel, EmailStr
from datetime import date


class CandidateBase(BaseModel):
    first_name: str
    last_name: str | None = None
    email: EmailStr
    phone_number: str | None = None
    workflow_id: int


class CandidateCreate(CandidateBase):
    pass  # resume will be uploaded as file


class CandidateOut(CandidateBase):
    id: int
    applied_date: date
    resume_url: str | None

    class Config:
        from_attributes  = True
