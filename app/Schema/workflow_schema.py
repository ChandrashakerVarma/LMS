from pydantic import BaseModel
from typing import Optional


class WorkflowBase(BaseModel):
    approval_status: str


class WorkflowCreate(WorkflowBase):
    posting_id: int


class WorkflowUpdate(BaseModel):
    approval_status: Optional[str] = None


class WorkflowResponse(WorkflowBase):
    id: int
    posting_id: int

    class Config:
        orm_mode = True
