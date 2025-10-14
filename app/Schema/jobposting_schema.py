from pydantic import BaseModel
from typing import Optional
from datetime import date


class UserRef(BaseModel):
    user_id: int
    name: str
    email: str


class JobPostingBase(BaseModel):
    role_id: int
    description_id: int
    number_of_positions: int
    employment_type: str
    location: str
    salary: Optional[float]
    posting_date: date
    closing_date: date


class JobPostingCreate(JobPostingBase):
    created_by_id: int


class JobPostingOut(JobPostingBase):
    position_id: int
    created_by: UserRef

    class Config:
        from_attributes = True
