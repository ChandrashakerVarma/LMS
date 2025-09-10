from pydantic import BaseModel
from typing import Optional, List

# Updated History schema (answer and result can be None)
class QuizHistoryResponse(BaseModel):
    id: int
    user_id: int
    answer: Optional[str] = None
    result: Optional[str] = None

    class Config:
        orm_mode = True

# Checkpoint schema
class QuizCheckpointResponse(BaseModel):
    id: int
    video_id: int
    timestamp: float
    question: str
    required: bool
    histories: Optional[List[QuizHistoryResponse]] = []  # Include related histories

    class Config:
        orm_mode = True

# Create schema for input
class QuizCheckpointCreate(BaseModel):
    video_id: int
    timestamp: float
    question: str
    required: bool
