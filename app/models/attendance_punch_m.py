# app/models/attendance_punch_m.py

from sqlalchemy import Column, Integer, String, Date, Time, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class AttendancePunch(Base):
    __tablename__ = "attendance_punches"

    id = Column(Integer, primary_key=True, index=True)

    # Biometric ID mapped to user table
    bio_id = Column(String(120), nullable=False)

    # Raw punch data from biometric device
    punch_date = Column(Date, nullable=False)
    punch_time = Column(Time, nullable=False)
    punch_type = Column(String(10), nullable=True)  # IN / OUT / NA

    # Audit time tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Audit users
    created_by = Column(String(100), nullable=True)   # current_user.name or system
    modified_by = Column(String(100), nullable=True)  # updated by which user/admin


 
