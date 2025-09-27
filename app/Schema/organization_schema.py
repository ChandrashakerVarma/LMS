from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schema.course_schema import CourseResponse
from app.schema.user_schema import UserResponse
from app.schema.branch_schema import BranchResponse  # import branch schema

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    branch_id: Optional[int]  # allow creating organization with branch

class OrganizationUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    branch_id: Optional[int]  # allow updating branch

class OrganizationResponse(OrganizationBase):
    id: int
    branch: Optional[BranchResponse] = None  # include branch in response
    created_at: datetime
    updated_at: datetime
    courses: Optional[List[CourseResponse]] = []
    users: Optional[List[UserResponse]] = []

    class Config:
        orm_mode = True
