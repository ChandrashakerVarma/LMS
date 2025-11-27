# app/schema/job_posting_schema.py

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class ApprovalStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# ------------------------------------------
# BASE SCHEMA
# ------------------------------------------
class JobPostingBase(BaseModel):
    job_description_id: int
    number_of_positions: int
    employment_type: str
    location: str
    salary: Optional[int] = None
    posting_date: date
    closing_date: Optional[date] = None


# ------------------------------------------
# CREATE
# ------------------------------------------
class JobPostingCreate(JobPostingBase):
    pass


# ------------------------------------------
# UPDATE
# ------------------------------------------
class JobPostingUpdate(BaseModel):
    number_of_positions: Optional[int] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[int] = None
    posting_date: Optional[date] = None
    closing_date: Optional[date] = None
    approval_status: Optional[ApprovalStatus] = None


# ------------------------------------------
# RESPONSE
# ------------------------------------------
class JobPostingResponse(JobPostingBase):
    id: int
    approval_status: ApprovalStatus
    created_by_id: int
    created_by_name: Optional[str]
    modified_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


# ------------------------------------------
# ACCEPTED CANDIDATE RESPONSE
# ------------------------------------------
class AcceptedCandidateResponse(BaseModel):
    candidate_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    job_posting_id: int
    job_role_id: int
    location: str
    status: str

    model_config = {
        "from_attributes": True
    }
