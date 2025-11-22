from sqlalchemy import Column, DateTime, Integer, String, Time, func
from sqlalchemy.orm import relationship
from app.database import Base


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    shift_name = Column(String(100), nullable=False, unique=True)  # restored
    description = Column(String(255), nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    shift_code = Column(String(50), unique=True, nullable=False)
    shift_type = Column(String(50), nullable=True)  # restored (Day/Night etc.)
    working_minutes = Column(Integer, nullable=False)
    lag_minutes = Column(Integer, default=60, nullable=False)
    status = Column(String(20), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

     # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationships
    user_shifts = relationship("UserShift", back_populates="shift", cascade="all, delete-orphan")
    permissions = relationship("Permission", back_populates="shift", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="shift", cascade="all, delete-orphan")
