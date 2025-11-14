from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    posting_id = Column(Integer, ForeignKey("job_postings.id"))
    approval_required = Column(Boolean, default=False)
    approver_id = Column(Integer, ForeignKey("users.id"))
    approval_status = Column(String, default="Pending")


    # Relationships
    approver = relationship("User", backref="workflows", foreign_keys=[approver_id])
    posting = relationship("JobPosting", backref="workflows")
    candidates = relationship("Candidate", back_populates="workflow")
