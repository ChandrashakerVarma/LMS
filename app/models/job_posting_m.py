from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    job_role_id = Column(Integer, ForeignKey("job_roles.id"), nullable=False)

    number_of_positions = Column(Integer, nullable=False)
    employment_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    salary = Column(Integer)
    posting_date = Column(Date, nullable=False)
    closing_date = Column(Date)

    # ---------------- Audit Fields ----------------
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # ---------------- Relationships ----------------
    jobrole = relationship("JobRole", back_populates="job_postings")
    candidates = relationship("Candidate", back_populates="job_posting")
