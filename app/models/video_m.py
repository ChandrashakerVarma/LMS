# app/models/video_m.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=True)
    youtube_url = Column(String(500), nullable=False)  # Content video link
    s3_key = Column(String(1024), nullable=True)       
    duration = Column(Float, nullable=True)  # Duration in minutes or seconds

    course = relationship("Course", back_populates="videos")
    checkpoints = relationship("QuizCheckpoint", back_populates="video", cascade="all, delete-orphan")
