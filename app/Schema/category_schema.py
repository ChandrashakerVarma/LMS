from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
<<<<<<< HEAD
from app.schema.course_schema import CourseResponse
=======
>>>>>>> origin/main

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

<<<<<<< HEAD
class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
=======

class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

>>>>>>> origin/main

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
<<<<<<< HEAD
    courses: Optional[List[CourseResponse]] = []

    class Config:
        from_attributes  = True
=======
    courses: Optional[List["CourseResponse"]] = []  # forward reference

    class Config:
        orm_mode = True


# ⚠️ Import CourseResponse **after** defining CategoryResponse
from app.schema.course_schema import CourseResponse
CategoryResponse.update_forward_refs()
>>>>>>> origin/main
