from pydantic import BaseModel
from typing import Optional

class CourseBase(BaseModel):
   
    title : str
    instructor : str
    level : str = "beginner"
    duration :  Optional[int] = None
    price : float = 0.0 

class CourseCreate(CourseBase):
        pass

class CourseResponse(CourseBase):
      id : int

class CourseUpdate(BaseModel):
      title: Optional[str] = None
      level: Optional[str] = None


class Config:
      orm_model = True
