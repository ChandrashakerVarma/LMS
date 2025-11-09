from pydantic import BaseModel, Field
from typing import Optional

# Schema for creating a checkpoint
class QuizCheckpointCreate(BaseModel):
    video_id: int
    timestamp: float
    question: str
    choices: str  # Can be a JSON string or comma-separated values
    correct_answer: str
    required: Optional[bool] = True

# Schema for updating a checkpoint
class QuizCheckpointUpdate(BaseModel):
    timestamp: Optional[float]
    question: Optional[str]
    choices: Optional[str]
    correct_answer: Optional[str]
    required: Optional[bool]

# Schema for returning a checkpoint
class QuizCheckpointResponse(BaseModel):
    id: int
    video_id: int
    timestamp: float
    question: str
    choices: str
    correct_answer: str
    required: bool

    class Config:
        from_attributes = True
