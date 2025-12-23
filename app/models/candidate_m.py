from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=True)

    # Basic info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    phone_number = Column(String(20), nullable=False)
    applied_date = Column(Date, nullable=False, default=datetime.utcnow)
    resume_url = Column(String(255))
    status = Column(String(20), default="Pending")  # Pending, Accepted, Rejected

    # Candidate type
    candidate_type = Column(String(20), nullable=False)   # fresher / experienced

    # Education / skills
    highest_qualification = Column(String(100), nullable=True)
    skills = Column(Text, nullable=True)

    # ----- Fresher Fields -----
    college_name = Column(String(150), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    course = Column(String(100), nullable=True)
    cgpa = Column(String(10), nullable=True)

    # ----- Experienced Fields -----
    total_experience = Column(String(20), nullable=True)
    previous_company = Column(String(150), nullable=True)
    last_ctc = Column(Integer, nullable=True)
    
    # ----- Language Levels -----
    telugu_level = Column(String(20), nullable=True)
    english_level = Column(String(20), nullable=True)
    hindi_level = Column(String(20), nullable=True)

    # Personal details
    gender = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    

    # Address fields
    address_line1 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationships
    job_posting = relationship("JobPosting", back_populates="candidates")
    documents = relationship("CandidateDocument", back_populates="candidate", cascade="all, delete-orphan")
