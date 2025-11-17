from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class QuizHistory(Base):
    __tablename__ = "quiz_histories"

    id = Column(Integer, primary_key=True, index=True)
    checkpoint_id = Column(Integer, ForeignKey("quiz_checkpoints.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)  # ✅ video link
    question = Column(String(500), nullable=True)  # question at submission
    answer = Column(String(500), nullable=True)
    result = Column(String(50), nullable=True)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())  # timestamp

    # Relationships
    checkpoint = relationship("QuizCheckpoint", back_populates="histories")
    video = relationship("Video")
