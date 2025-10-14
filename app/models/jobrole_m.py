# app/models/job_role_m.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    required_skills = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # ✅ Relationship to job postings via role_id
    job_postings = relationship(
        "JobPosting",
        back_populates="role",
        cascade="all, delete-orphan",
        foreign_keys="[JobPosting.role_id]"
    )

    # ✅ Optional second relationship using description_id
    # Add `overlaps` to avoid SAWarning
    job_postings_by_description = relationship(
        "JobPosting",
        foreign_keys="[JobPosting.description_id]",
        overlaps="description"
    )
