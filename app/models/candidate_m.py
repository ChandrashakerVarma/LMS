from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    applied_date = Column(Date, nullable=False)
    resume_url = Column(String(255), nullable=True)

    workflow = relationship("Workflow", back_populates="candidates")
    documents = relationship("CandidateDocument", back_populates="candidate", cascade="all, delete-orphan")
