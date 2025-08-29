from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, unique=True)
    instructor = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False, default="beginner")
    duration = Column(Integer, nullable=True)
    price = Column(Float, default=0.0)


    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
