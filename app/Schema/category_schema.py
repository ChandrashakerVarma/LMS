from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    courses: Optional[List["CourseResponse"]] = []  # forward ref

    class Config:
        from_attributes = True  # Pydantic v1
        

# Import the referenced model AFTER defining CategoryResponse
from app.schema.course_schema import CourseResponse

# Resolve forward references for Pydantic v1
CategoryResponse.update_forward_refs()
