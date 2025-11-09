# app/models/quiz_history_m.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class QuizHistory(Base):
    __tablename__ = "quiz_histories"

    id = Column(Integer, primary_key=True, index=True)
    checkpoint_id = Column(Integer, ForeignKey("quiz_checkpoints.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    question = Column(String(500), nullable=True)  # ✅ Add this field to store the question at submission time
    answer = Column(String(500), nullable=True)
    result = Column(String(50), nullable=True)
    

    # Relationships
    checkpoint = relationship("QuizCheckpoint", back_populates="histories")
