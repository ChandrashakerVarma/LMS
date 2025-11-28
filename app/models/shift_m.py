from enum import Enum
from sqlalchemy import Column, DateTime, Integer, String, Time, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)

    # Manager who created the shift (FK)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    shift_name = Column(String(100), nullable=False, unique=True)
    shift_code = Column(String(50), unique=True, nullable=False)
    shift_type = Column(String(50), nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    working_minutes = Column(Integer, nullable=False)
    lag_minutes = Column(Integer, default=60, nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(20), default="active")
    is_week_off = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_manager = relationship("User", back_populates="created_shifts")
    permissions = relationship("Permission", back_populates="shift", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="shift", cascade="all, delete-orphan")
    shift_roster_details = relationship("ShiftRosterDetail", back_populates="shift")
    user_shifts = relationship("UserShift", back_populates="shift")

    # Audit fields
    modified_by = Column(String(100), nullable=True)
