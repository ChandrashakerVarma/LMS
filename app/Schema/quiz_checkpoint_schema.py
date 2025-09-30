# app/schema/quiz_checkpoint_schema.py
from pydantic import BaseModel
from typing import Optional

class QuizCheckpointCreate(BaseModel):
    video_id: int
    course_id: int
    timestamp: float
    question: str
    choices: str
    correct_answer: str
    required: Optional[bool] = True

class QuizCheckpointUpdate(BaseModel):
    video_id: Optional[int]
    course_id: Optional[int]
    timestamp: Optional[float]
    question: Optional[str]
    choices: Optional[str]
    correct_answer: Optional[str]
    required: Optional[bool]

class QuizCheckpointResponse(BaseModel):
    id: int
    video_id: int
    course_id: int
    timestamp: float
    question: str
    choices: str
    correct_answer: str
    required: bool

    class Config:
        orm_mode = True
