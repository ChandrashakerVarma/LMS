# app/models/quiz_checkpoint_m.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class QuizCheckpoint(Base):
    __tablename__ = "quiz_checkpoints"

    id = Column(Integer, primary_key=True, index=True)  # Unique question ID
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(Float, nullable=False)  # Time in seconds or minutes
    question = Column(String(500), nullable=False)
    choices = Column(String(500), nullable=False)  # Store choices as JSON string or comma-separated
    correct_answer = Column(String(50), nullable=False)  # Correct choice
    required = Column(Boolean, default=True)

    video = relationship("Video", back_populates="checkpoints")
    histories = relationship("QuizHistory", back_populates="checkpoint", cascade="all, delete-orphan")
