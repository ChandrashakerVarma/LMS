from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.database import Base


# ----------------------------------------------------
# APPROVAL STATUS ENUM
# ----------------------------------------------------
class ApprovalStatus(str, PyEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# ----------------------------------------------------
# JOB TYPE ENUM (fresher / experienced / both)
# ----------------------------------------------------
class JobType(str, PyEnum):
    fresher = "fresher"
    experienced = "experienced"
    both = "both"


# ----------------------------------------------------
# JOB POSTING MODEL
# ----------------------------------------------------
class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)

    # fresher / experienced / both
    job_type = Column(Enum(JobType), nullable=False)
    number_of_positions = Column(Integer, nullable=False)
    employment_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    salary = Column(Integer)

    posting_date = Column(Date, nullable=False)
    closing_date = Column(Date)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.accepted, nullable=False)

    # Relationships
    job_description = relationship("JobDescription", back_populates="job_postings")
    candidates = relationship("Candidate", back_populates="job_posting")
    organization = relationship("Organization", back_populates="job_postings")
    branch = relationship("Branch", back_populates="job_postings")
