from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# ---------------- JobRole ----------------
class JobRoleOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    required_skills: Optional[str]

    class Config:
        orm_mode = True


# ---------------- Workflow ----------------
class WorkflowOut(BaseModel):
    id: int
    approval_status: str

    class Config:
        orm_mode = True


# ---------------- Candidate ----------------
class CandidateOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    status: str

    class Config:
        orm_mode = True


# ---------------- Base ----------------
class JobPostingBase(BaseModel):
    job_role_id: int
    number_of_positions: int
    employment_type: str
    location: str
    salary: Optional[int]
    posting_date: date
    closing_date: Optional[date]


# ---------------- Create ----------------
class JobPostingCreate(JobPostingBase):
    pass


# ---------------- Update ----------------
class JobPostingUpdate(BaseModel):
    job_role_id: Optional[int]
    number_of_positions: Optional[int]
    employment_type: Optional[str]
    location: Optional[str]
    salary: Optional[int]
    posting_date: Optional[date]
    closing_date: Optional[date]


# ---------------- Output ----------------
class JobPostingOut(JobPostingBase):
    id: int
    jobrole: Optional[JobRoleOut]
    workflow: Optional[WorkflowOut]
    candidates: Optional[List[CandidateOut]]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    class Config:
        orm_mode = True
