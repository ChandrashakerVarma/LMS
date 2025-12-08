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

    model_config = {"from_attributes": True}

# Import referenced model AFTER defining CategoryResponse
from app.schema.course_schema import CourseResponse

# Use model_rebuild() instead of update_forward_refs()
CategoryResponse.model_rebuild()
