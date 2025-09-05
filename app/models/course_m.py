from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, unique=True)
    instructor = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False, default="beginner")
    youtube_url = Column(String(500), nullable=False)  # required YouTube link
    duration = Column(Integer, nullable=True)
    price = Column(Float, default=0.0)


    created_at = Column(DateTime, server_default=func.now(), nullable= False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Course id={self.id} title={self.title!r} instructor={self.instructor!r}>"
    
    #relationship with progress
    progress_records = relationship("Progress", back_populates="course", cascade="all, delete")
    progress = relationship("Progress", back_populates="course")
