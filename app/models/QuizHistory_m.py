# app/models/QuizHistory_m.py
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class QuizHistory(Base):
    __tablename__ = "quiz_histories"

    id = Column(Integer, primary_key=True, index=True)
    checkpoint_id = Column(Integer, ForeignKey("quiz_checkpoints.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    answer = Column(String(500), nullable=True)   # optional
    result = Column(String(50), nullable=True)    # optional
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)  # ✅ Add this

    # Relationships
    checkpoint = relationship("QuizCheckpoint", back_populates="histories")
