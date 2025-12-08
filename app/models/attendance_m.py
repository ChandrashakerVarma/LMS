from sqlalchemy import (
    Column, Integer, DateTime, String, Float, ForeignKey, Date, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)

    # Employee / Shift
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)   # IMPORTANT

    # Real-time Check-in
    check_in_time = Column(DateTime, nullable=True)
    check_in_lat = Column(Float, nullable=True)
    check_in_long = Column(Float, nullable=True)
    gps_score = Column(Float, nullable=True)
    location_status = Column(String(50), nullable=True)

    is_face_verified = Column(Integer, default=0)
    face_confidence = Column(Float, nullable=True)
    check_in_image_path = Column(String(255), nullable=True)

    anomaly_flag = Column(String(20), default="LOW")

    punch_out = Column(DateTime, nullable=True)
    total_worked_minutes = Column(Integer, nullable=True)
    status = Column(String(20), nullable=True)

    # Monthly Stats
    month = Column(Date, nullable=True, index=True)

    total_days = Column(Integer, default=0)
    present_days = Column(Integer, default=0)
    absent_days = Column(Integer, default=0)
    half_days = Column(Integer, default=0)
    holidays = Column(Integer, default=0)
    sundays = Column(Integer, default=0)
    leaves = Column(Integer, default=0)
    permissions = Column(Integer, default=0)

    # Payroll
    total_work_minutes = Column(Integer, default=0)
    overtime_minutes = Column(Integer, default=0)
    late_minutes = Column(Integer, default=0)
    early_exit_minutes = Column(Integer, default=0)

    summary_status = Column(String(30), default="Pending")

    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now(), nullable=True)

    # Relationships
    user = relationship("User", back_populates="attendances")
    shift = relationship("Shift")                       # ADD THIS
