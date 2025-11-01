from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from schema.course_schema import CourseResponse

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
    courses: Optional[List["CourseResponse"]] = []  # forward reference

    class Config:
        from_attributes = True
