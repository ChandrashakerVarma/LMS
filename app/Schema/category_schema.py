from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.schema.course_schema import CourseResponse


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
        from_attributes = True  # Pydantic v2

# Import the referenced model AFTER defining CategoryResponse
from app.schema.course_schema import CourseResponse

# Rebuild models to resolve forward references (Pydantic v2)
CategoryResponse.model_rebuild()
