from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CandidateDocument(Base):
    __tablename__ = "candidate_documents"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    document_type = Column(String(100), nullable=False)
    document_url = Column(String(255), nullable=False)

    # Relationship to Candidate model
    candidate = relationship("Candidate", back_populates="documents")
