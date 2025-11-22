from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    applied_date = Column(Date, nullable=False)
    resume_url = Column(String(255))    

    status = Column(String(20), default="Pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)
    # Possible values → Pending, Approved, Rejected

    # ---------------- Relationships ----------------
    job_posting = relationship("JobPosting", back_populates="candidates")
    documents = relationship("CandidateDocument", back_populates="candidate", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="candidate")
