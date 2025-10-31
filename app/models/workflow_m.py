from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    approval_required = Column(Boolean, default=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_status = Column(String(50), default="Pending")
    posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)

    # Relationships
    approver = relationship("User", backref="workflows", foreign_keys=[approver_id])
    posting = relationship("JobPosting", backref="workflows")
    candidates = relationship("Candidate", back_populates="workflow")
