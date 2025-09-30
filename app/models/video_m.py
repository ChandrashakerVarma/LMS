# app/models/video_m.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    youtube_url = Column(String(500), nullable=False)
    duration = Column(Float, nullable=False, default=0.0)

    course = relationship("Course", back_populates="videos")
    checkpoints = relationship("QuizCheckpoint", back_populates="video", cascade="all, delete-orphan")
    quiz_histories = relationship("QuizHistory", back_populates="video", cascade="all, delete-orphan")
