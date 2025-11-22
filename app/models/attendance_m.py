# app/models/attendance_m.py
from sqlalchemy import Column, Integer, Date, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)

    attendance_date = Column(Date, nullable=False)  # Always shift start date
    punch_in = Column(DateTime, nullable=False)
    punch_out = Column(DateTime, nullable=False)
    total_worked_minutes = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="Pending")  # Full Day / Half Day / Absent

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)



    # Relationships
    user = relationship("User", back_populates="attendances")
    shift = relationship("Shift")
