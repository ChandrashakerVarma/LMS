# app/models/branch_m.py
<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
=======
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
>>>>>>> origin/main
from sqlalchemy.orm import relationship
from app.database import Base

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    name = Column(String(150), nullable=False, unique=True)
    address = Column(String(255), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="branches")
    users = relationship("User", back_populates="branch", cascade="all, delete-orphan")  # ✅ new
    courses = relationship("Course", back_populates="branch", cascade="all, delete-orphan")  # ✅ new

=======
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        server_onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="branches")
    courses = relationship("Course", back_populates="branch", cascade="all, delete-orphan")
    users = relationship("User", back_populates="branch", cascade="all, delete-orphan")
>>>>>>> origin/main

