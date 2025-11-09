from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    joining_date = Column(Date, nullable=True)
    relieving_date = Column(Date, nullable=True)

    address = Column(String(255), nullable=True)
    designation = Column(String(100), nullable=True)
    inactive = Column(Boolean, default=False)

    biometric_id = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="users")
    branch = relationship("Branch", back_populates="users", lazy="joined")
    organization = relationship("Organization", back_populates="users", lazy="joined")
    progress = relationship("Progress", back_populates="user")
    enrollments = relationship("Enrollment", back_populates="user")
    permissions = relationship("Permission", back_populates="users")
    # Links to other models
    leaves = relationship("LeaveMaster", back_populates="user", cascade="all, delete-orphan")
    user_shifts = relationship("UserShift", back_populates="user", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    job_postings = relationship("JobPosting", back_populates="user")
    shift_change_requests = relationship("ShiftChangeRequest", back_populates="user")
