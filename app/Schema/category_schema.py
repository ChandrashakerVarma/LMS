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
    courses: Optional[List["CourseResponse"]] = []  # forward reference

    class Config:
        orm_mode = True


# ⚠️ Import CourseResponse **after** defining CategoryResponse
from app.schema.course_schema import CourseResponse
CategoryResponse.update_forward_refs()
