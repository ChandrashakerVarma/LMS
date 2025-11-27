from pydantic import BaseModel

class NotificationBase(BaseModel):
    candidate_id: int
    message: str


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int

    class Config:
        orm_mode = True
