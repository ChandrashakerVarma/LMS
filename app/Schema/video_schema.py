from pydantic import BaseModel, HttpUrl
from typing import List, Optional
<<<<<<< HEAD
from app.schema.quiz_checkpoint_schema import QuizCheckpointResponse

=======
from datetime import datetime
from app.schema.quiz_checkpoint_schema import QuizCheckpointResponse  # Import checkpoints
>>>>>>> origin/main

class VideoBase(BaseModel):
    title: Optional[str]
    youtube_url: str
    duration: Optional[float] = 0.0

class VideoCreate(VideoBase):
    course_id: int

<<<<<<< HEAD
# Update Schema
# ----------------------
class VideoUpdate(BaseModel):
    title: Optional[str] 
=======
class VideoUpdate(BaseModel):
    title: Optional[str]
>>>>>>> origin/main
    youtube_url: Optional[HttpUrl] = None
    duration: Optional[float] = 0.0

class VideoResponse(VideoBase):
    id: int
    course_id: int
<<<<<<< HEAD
    checkpoints: Optional[List[QuizCheckpointResponse]] = []  # Add checkpoints here


    class Config:
        from_attributes  = True
=======
    checkpoints: List[QuizCheckpointResponse] = []  # Bind checkpoints
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
>>>>>>> origin/main
