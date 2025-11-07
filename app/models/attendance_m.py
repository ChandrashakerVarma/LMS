# app/models/attendance_m.py
from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)

    punch_in = Column(DateTime, nullable=False)
    punch_out = Column(DateTime, nullable=False)
    total_worked_minutes = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # Full Day / Half Day / Absent

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="attendances")
    shift = relationship("Shift")
