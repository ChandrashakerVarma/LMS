from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    number_of_positions = Column(Integer)
    employment_type = Column(String(50))
    location = Column(String(100))
    salary = Column(Integer)
    posting_date = Column(Date)
    closing_date = Column(Date)
    description_id = Column(Integer, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships (optional, if these tables exist)
    role = relationship("Role", back_populates="job_postings", lazy="joined")
    created_by = relationship("User", back_populates="job_postings", lazy="joined")
    

    user = relationship("User", back_populates="job_postings", overlaps="created_by")
