# app/schema/video_schema.py
from pydantic import BaseModel, HttpUrl
from typing import Optional

class VideoBase(BaseModel):
    title: Optional[str] = None
    youtube_url: Optional[HttpUrl] = None
    s3_key: Optional[str] = None
    duration: Optional[float] = None

class VideoCreate(VideoBase):
    course_id: int
    youtube_url: Optional[str] = None

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    youtube_url: Optional[HttpUrl] = None
    s3_key: Optional[str] = None
    duration: Optional[float] = None

class VideoResponse(VideoBase):  # ✅ renamed from VideoOut
    id: int
    course_id: int

    class Config:
        from_attributes = True
