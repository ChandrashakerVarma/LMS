from pydantic import BaseModel
from datetime import datetime

# Used for creating a progress record
class ProgressCreate(BaseModel):
    course_id: int
    watched_minutes: float = 0.0
    progress_percentage: float = 0.0

# Used for updating progress
class ProgressUpdate(BaseModel):
    watched_minutes: float
    progress_percentage: float

# Used for responses
class ProgressResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    watched_minutes: float
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True   # ✅ Required for SQLAlchemy -> Pydantic
