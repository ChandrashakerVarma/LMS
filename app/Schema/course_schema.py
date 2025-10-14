from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schema.video_schema import VideoResponse  # ✅ Import VideoResponse

class CourseBase(BaseModel):
    title: str
    instructor: str
    level: Optional[str] = "beginner"
    price: Optional[float] = 0.0
    organization_id: Optional[int]
    branch_id: Optional[int]       # new
    category_id: Optional[int]

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str]
    instructor: Optional[str]
    level: Optional[str]
    price: Optional[float]
    organization_id: Optional[int]
    branch_id: Optional[int]       # new
    category_id: Optional[int]

class CourseResponse(CourseBase):
    id: int
    videos: List[VideoResponse] = []
    duration: Optional[float] = 0.0

    class Config:
        from_attributes = True
