from pydantic import BaseModel
from typing import Optional

class WorkflowBase(BaseModel):
    approval_required: bool = False
    approver_id: Optional[int] = None
    approval_status: Optional[str] = "Pending"
    posting_id: int


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    id: int

    class Config:
        orm_mode = True
