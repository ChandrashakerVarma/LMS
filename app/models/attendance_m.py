from sqlalchemy import Column, Integer, Date, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(Date, nullable=False, index=True)

    total_days = Column(Integer, default=0)
    present_days = Column(Integer, default=0)
    absent_days = Column(Integer, default=0)
    half_days = Column(Integer, default=0)
    holidays = Column(Integer, default=0)
    sundays = Column(Integer, default=0)
    leaves = Column(Integer, default=0)
    permissions = Column(Integer, default=0)

    total_work_minutes = Column(Integer, default=0)
    overtime_minutes = Column(Integer, default=0)
    late_minutes = Column(Integer, default=0)
    early_exit_minutes = Column(Integer, default=0)

    summary_status = Column(String(30), default="Pending")

    # FIXED — updated_at should NOT get default
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now(), nullable=True)

    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    user = relationship("User", back_populates="monthly_attendance")
