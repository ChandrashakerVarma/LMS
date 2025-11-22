from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    required_skills = Column(String(1000))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

     # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)


    job_postings = relationship("JobPosting", back_populates="jobrole")
