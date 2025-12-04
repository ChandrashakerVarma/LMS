from datetime import datetime
from pydantic import BaseModel


class UserFaceBase(BaseModel):
    model_name: str | None = "face_recognition_resnet"


class UserFaceRead(UserFaceBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
