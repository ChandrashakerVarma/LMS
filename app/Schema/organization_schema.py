# app/schema/organization_schema.py
from pydantic import BaseModel
from typing import Optional, List
from app.schema.course_schema import CourseResponse
from app.schema.user_schema import UserResponse

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

class OrganizationResponse(OrganizationBase):
    id: int
    courses: Optional[List[CourseResponse]] = []
    users: Optional[List[UserResponse]] = []

    class Config:
        orm_mode = True
