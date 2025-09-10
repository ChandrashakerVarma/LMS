from pydantic import BaseModel
from datetime import datetime

class QuizHistoryBase(BaseModel):
    user_id: int
    checkpoint_id: int
    score: float

class QuizHistoryCreate(QuizHistoryBase):
    pass

# Custom response model with message
class QuizHistoryMessageResponse(BaseModel):
    message: str
    id: int
    user_id: int
    checkpoint_id: int
    score: float = 0
    completed_at: datetime

    class Config:
        orm_mode = True

class QuizHistoryResponse(QuizHistoryBase):
    id: int
    completed_at: datetime

    class Config:
        orm_mode = True

