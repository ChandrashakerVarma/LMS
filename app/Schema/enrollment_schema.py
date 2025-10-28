from pydantic import BaseModel
from datetime import datetime

class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime

    class Config:
<<<<<<< HEAD
        from_attributes = True
=======
        orm_mode = True
>>>>>>> origin/main
