from pydantic import BaseModel
from datetime import datetime

# Used for updating progress after video/quiz checkpoint
class ProgressUpdateSchema(BaseModel):
    user_id: int
    course_id: int
    watched_minutes: float  # frontend sends current watched minutes

# Response
class ProgressResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    watched_minutes: float
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

    class Config:
<<<<<<< HEAD
        from_attributes = True
=======
        orm_mode = True
>>>>>>> origin/main
