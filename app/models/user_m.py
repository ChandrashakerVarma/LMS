# app/models/user_m.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship,declarative_base
from app.database import Base
from app.models.organization import Organization


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    inactive = Column(Boolean, default=False)

    # Relationships
    role = relationship("Role", back_populates="users", lazy="joined")
    organization = relationship(Organization, back_populates="users")
    progress = relationship("Progress", back_populates="user", lazy="selectin")
    enrollments = relationship("Enrollment", back_populates="user")
