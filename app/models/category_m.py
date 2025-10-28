# app/models/category_m.py
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
<<<<<<< HEAD
=======
    
>>>>>>> origin/main

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)

    # Relationships
<<<<<<< HEAD
    courses = relationship("Course", back_populates="category", cascade="all, delete-orphan")
=======
    courses = relationship("Course", back_populates="category", cascade="all, delete-orphan")
>>>>>>> origin/main
