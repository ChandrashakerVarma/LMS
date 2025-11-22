from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.database import Base

class ApprovalStatus(str, PyEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)
    posting_id = Column(Integer, ForeignKey("job_postings.id"))
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.pending)

