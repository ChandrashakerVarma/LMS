from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Progress(Base):   
    __tablename__ = "progress"  

    id = Column(Integer, primary_key=True, index= True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable= False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable= False)
    watched_minutes = Column(Float, default=0.0)   # how much user watched
    progress_percentage = Column(Float, default=0.0)   # 0.0 → 100.0

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #relatonships
    user = relationship("User", back_populates="progress")
    course = relationship("Course", back_populates="progress")

  