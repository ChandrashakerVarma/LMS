from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String, func
from sqlalchemy.orm import relationship
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    punch_id = Column(String(100), nullable=False)

    first_punch = Column(DateTime, nullable=True)
    last_punch = Column(DateTime, nullable=True)
    shift_start = Column(DateTime, nullable=True)
    shift_end = Column(DateTime, nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(50), nullable=True)  # e.g. Full-day / Half-day / Absent / Pending

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="attendances")
