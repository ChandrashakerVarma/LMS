from pydantic import BaseModel
from typing import Optional
from datetime import date

# ✅ Schema for creating a new Job Posting
class JobPostingCreate(BaseModel):
    role_id: int
    number_of_positions: int
    employment_type: str
    location: str
    salary: float
    posting_date: date
    closing_date: date
    description_id: int
    created_by_id: int

    class Config:
        from_attributes = True


# ✅ Schema for reading Job Posting (response)
class JobPostingOut(BaseModel):
    id: int
    role_id: int
    number_of_positions: int
    employment_type: str
    location: str
    salary: float
    posting_date: date
    closing_date: date
    description_id: int
    created_by_id: int

    class Config:
        from_attributes = True
