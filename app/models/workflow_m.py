from sqlalchemy import Column, Integer, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ApprovalStatus(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    approval_required = Column(Boolean, default=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.Pending)

    job_posting = relationship("JobPosting", back_populates="workflows")
    approver = relationship("User")
    candidates = relationship("Candidate", back_populates="workflow")