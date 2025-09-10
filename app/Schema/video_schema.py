from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class VideoBase(BaseModel):
    title: Optional[str]
    youtube_url: str
    duration: Optional[float] = 0.0

class VideoCreate(VideoBase):
    course_id: int

# Update Schema
# ----------------------
class VideoUpdate(BaseModel):
    title: Optional[str] 
    youtube_url: Optional[HttpUrl] = None
    duration: Optional[float] = 0.0

class VideoResponse(VideoBase):
    id: int
    course_id: int

    class Config:
        orm_mode = True
