from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CandidateDocument(Base):
    __tablename__ = "candidate_documents"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    document_type = Column(String(50), nullable=False)  # e.g., "resume", "cover_letter", "certificate"
    document_url = Column(String(500), nullable=False)  # S3 link

    candidate = relationship("Candidate", back_populates="documents")
