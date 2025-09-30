from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QuizHistoryBase(BaseModel):
    user_id: int
    checkpoint_id: int
    course_id: int
    video_id: int   # ✅ new field
    answer: Optional[str] = None
    result: Optional[str] = None
    question: Optional[str] = None


class QuizHistoryCreate(QuizHistoryBase):
    pass


# Custom response model with message
class QuizHistoryMessageResponse(BaseModel):
    message: str
    id: int
    user_id: int
    checkpoint_id: int
    course_id: int
    video_id: int   # ✅ new field
    answer: Optional[str] = None
    result: Optional[str] = None
    question: Optional[str] = None
    completed_at: datetime

    class Config:
        orm_mode = True


class QuizHistoryResponse(QuizHistoryBase):
    id: int
    completed_at: datetime

    class Config:
        orm_mode = True
