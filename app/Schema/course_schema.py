# app/schema/course_schema.py
from pydantic import BaseModel
from typing import List, Optional
from app.schema.video_schema import VideoResponse

class CourseBase(BaseModel):
    title: str
    instructor: str
    level: Optional[str] = "beginner"
    
    price: Optional[float] = 0.0
    organization_id: Optional[int]  # new


class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str]
    instructor: Optional[str]
    level: Optional[str]
    price: Optional[float]
    organization_id: Optional[int]  # new


class CourseResponse(CourseBase):
    id: int
    videos: List[VideoResponse] = []
    duration: Optional[float] = 0.0

    class Config:
        orm_mode = True
