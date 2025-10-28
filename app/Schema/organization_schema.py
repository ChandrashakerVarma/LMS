# app/schema/organization_schema.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schema.course_schema import CourseResponse
from app.schema.user_schema import UserResponse
from app.schema.branch_schema import BranchResponse

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    branch_ids: Optional[List[int]] = []  # allow creating org with multiple branches

class OrganizationUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    branch_ids: Optional[List[int]] = []

class OrganizationResponse(OrganizationBase):
    id: int
    branches: List[BranchResponse] = []  # list of branches
    created_at: datetime
    updated_at: datetime
    courses: Optional[List[CourseResponse]] = []
    users: Optional[List[UserResponse]] = []

    class Config:
<<<<<<< HEAD
        from_attributes = True
=======
        orm_mode = True
>>>>>>> origin/main
