from pydantic import BaseModel
from datetime import date

class CandidateBase(BaseModel):
    first_name: str
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    workflow_id: int | None = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    workflow_id: int | None = None

class CandidateOut(CandidateBase):
    id: int
    applied_date: date
    resume_url: str | None = None

    class Config:
        from_attributes = True
