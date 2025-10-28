from pydantic import BaseModel
<<<<<<< HEAD
from typing import Optional, List
from datetime import datetime
from app.schema.video_schema import VideoResponse  # ✅ Import VideoResponse
=======
from typing import List, Optional
from app.schema.video_schema import VideoResponse  # videos are fine
>>>>>>> origin/main

class CourseBase(BaseModel):
    title: str
    instructor: str
    level: Optional[str] = "beginner"
    price: Optional[float] = 0.0
<<<<<<< HEAD
    organization_id: Optional[int]
    branch_id: Optional[int]       # new
    category_id: Optional[int]
=======
    category_id: Optional[int] = None  # link to category
>>>>>>> origin/main

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
<<<<<<< HEAD
    title: Optional[str]
    instructor: Optional[str]
    level: Optional[str]
    price: Optional[float]
    organization_id: Optional[int]
    branch_id: Optional[int]       # new
    category_id: Optional[int]
=======
    title: Optional[str] = None
    instructor: Optional[str] = None
    level: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
>>>>>>> origin/main

class CourseResponse(CourseBase):
    id: int
    videos: List[VideoResponse] = []
    duration: Optional[float] = 0.0
<<<<<<< HEAD

    class Config:
        from_attributes = True
=======
    category: Optional["CategoryResponse"] = None  # forward ref as string

    class Config:
        orm_mode = True

# ⚠️ resolve forward references at the end
from app.schema.category_schema import CategoryResponse
CourseResponse.update_forward_refs()
>>>>>>> origin/main
