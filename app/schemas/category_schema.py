from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ----------------------------------------------------
# Base Schema
# ----------------------------------------------------
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ----------------------------------------------------
# Response Schema (with forward ref)
# ----------------------------------------------------
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    courses: Optional[List["CourseResponse"]] = []

    model_config = {"from_attributes": True}   # Pydantic v2
    


# Pydantic v2 FIX:
# Import AFTER models are declared
from app.schemas.course_schema import CourseResponse

# Rebuild forward references
CategoryResponse.model_rebuild()
