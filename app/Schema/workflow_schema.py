from pydantic import BaseModel
from enum import Enum


class ApprovalStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class WorkflowBase(BaseModel):
    posting_id: int
    approval_required: bool
    approver_id: int


class WorkflowCreate(WorkflowBase):
    approval_status: ApprovalStatus = ApprovalStatus.Pending


class WorkflowOut(WorkflowBase):
    id: int
    approval_status: ApprovalStatus

    class Config:
        from_attributes = True
