from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.Schema.course_schema import CourseResponse


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
        orm_mode = True  # ✅ Pydantic v1 compatible


# ✅ Add this at the bottom (after all class definitions)
from app.Schema.course_schema import CourseResponse
CategoryResponse.update_forward_refs(CourseResponse=CourseResponse)
