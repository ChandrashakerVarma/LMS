# app/models/job_posting_m.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("job_roles.id"), nullable=False)
    description_id = Column(Integer, ForeignKey("job_roles.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    number_of_positions = Column(Integer, nullable=False)
    employment_type = Column(String(50), nullable=False)
    location = Column(String(150), nullable=False)
    salary = Column(Float, nullable=True)
    posting_date = Column(Date, nullable=False)
    closing_date = Column(Date, nullable=False)

    # ✅ Correct FK relationship
    role = relationship(
        "JobRole",
        back_populates="job_postings",
        foreign_keys=[role_id]
    )

    # ✅ Secondary link to JobRole by description_id
    # Add `overlaps` to silence duplicate-FK warnings
    description = relationship(
        "JobRole",
        foreign_keys=[description_id],
        overlaps="job_postings_by_description"
    )

    workflows = relationship("Workflow", back_populates="job_posting")
