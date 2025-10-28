from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QuizHistoryBase(BaseModel):
    user_id: int
    checkpoint_id: int
    course_id: int
<<<<<<< HEAD
    video_id: int   # ✅ new field
=======
    video_id: int  # ✅ add video_id
>>>>>>> origin/main
    answer: Optional[str] = None
    result: Optional[str] = None
    question: Optional[str] = None

<<<<<<< HEAD

class QuizHistoryCreate(QuizHistoryBase):
    pass


# Custom response model with message
=======
class QuizHistoryCreate(QuizHistoryBase):
    pass

# Response with message
>>>>>>> origin/main
class QuizHistoryMessageResponse(BaseModel):
    message: str
    id: int
    user_id: int
    checkpoint_id: int
    course_id: int
<<<<<<< HEAD
    video_id: int   # ✅ new field
=======
    video_id: int  # ✅ add video_id
>>>>>>> origin/main
    answer: Optional[str] = None
    result: Optional[str] = None
    question: Optional[str] = None
    completed_at: datetime

    class Config:
<<<<<<< HEAD
        from_attributes  = True

=======
        orm_mode = True
>>>>>>> origin/main

class QuizHistoryResponse(QuizHistoryBase):
    id: int
    completed_at: datetime

    class Config:
<<<<<<< HEAD
        from_attributes = True
=======
        orm_mode = True
>>>>>>> origin/main
