# app/models/quiz_checkpoint_m.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class QuizCheckpoint(Base):
    __tablename__ = "quiz_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)  # ✅ new
    timestamp = Column(Float, nullable=False)
    question = Column(String(500), nullable=False)
    choices = Column(String(500), nullable=False)
    correct_answer = Column(String(50), nullable=False)
    required = Column(Boolean, default=True)

    video = relationship("Video", back_populates="checkpoints")
    course = relationship("Course", back_populates="checkpoints")  # ✅ new relationship
    histories = relationship("QuizHistory", back_populates="checkpoint", cascade="all, delete-orphan")
