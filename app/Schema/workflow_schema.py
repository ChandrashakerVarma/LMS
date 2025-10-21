from pydantic import BaseModel
from enum import Enum
from typing import Optional


# Enum for approval status
class ApprovalStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


# Shared base fields
class WorkflowBase(BaseModel):
    posting_id: int
    approval_required: bool
    approver_id: int


# For creating a new workflow
class WorkflowCreate(WorkflowBase):
    approval_status: ApprovalStatus = ApprovalStatus.Pending


# For updating an existing workflow
class WorkflowUpdate(BaseModel):
    posting_id: Optional[int] = None
    approval_required: Optional[bool] = None
    approver_id: Optional[int] = None
    approval_status: Optional[ApprovalStatus] = None


# For returning workflow data (read responses)
class WorkflowOut(WorkflowBase):
    id: int
    approval_status: ApprovalStatus

    class Config:
        from_attributes = True  # ✅ same as orm_mode=True in newer Pydantic versions

