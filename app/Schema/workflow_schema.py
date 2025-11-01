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

class WorkflowOut(WorkflowBase):
    id: int

    model_config = {
        "from_attributes": True  # replaces orm_mode in Pydantic v2
    }
