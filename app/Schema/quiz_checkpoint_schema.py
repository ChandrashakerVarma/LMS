<<<<<<< HEAD
# app/schema/quiz_checkpoint_schema.py
from pydantic import BaseModel
from typing import Optional

class QuizCheckpointCreate(BaseModel):
    video_id: int
    course_id: int
=======
from pydantic import BaseModel, Field
from typing import Optional

# Schema for creating a checkpoint
class QuizCheckpointCreate(BaseModel):
    course_id: int  # ✅ course link
    video_id: int
>>>>>>> origin/main
    timestamp: float
    question: str
    choices: str
    correct_answer: str
    required: Optional[bool] = True

<<<<<<< HEAD
class QuizCheckpointUpdate(BaseModel):
    video_id: Optional[int]
    course_id: Optional[int]
=======
# Schema for updating a checkpoint
class QuizCheckpointUpdate(BaseModel):
    course_id: Optional[int]
    video_id: Optional[int]
>>>>>>> origin/main
    timestamp: Optional[float]
    question: Optional[str]
    choices: Optional[str]
    correct_answer: Optional[str]
    required: Optional[bool]

<<<<<<< HEAD
class QuizCheckpointResponse(BaseModel):
    id: int
    video_id: int
    course_id: int
=======
# Schema for returning a checkpoint
class QuizCheckpointResponse(BaseModel):
    id: int
    course_id: int  # ✅ course
    video_id: int
>>>>>>> origin/main
    timestamp: float
    question: str
    choices: str
    correct_answer: str
    required: bool

    class Config:
<<<<<<< HEAD
        from_attributes = True
=======
        orm_mode = True
>>>>>>> origin/main
