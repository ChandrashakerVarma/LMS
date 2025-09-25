# app/models/organization_m.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(String(500), nullable=True)

    # Relationships
    courses = relationship(
        "Course",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    users = relationship("User", back_populates="organization")
