from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(String(10), nullable=False)      # Example: "09:00"
    end_time = Column(String(10), nullable=False)        # Example: "18:00"
    shift_code = Column(String(20), unique=True, nullable=False)
    working_minutes = Column(Integer, nullable=False)
    status = Column(String(20), default="Active")        # Active / Inactive
    is_rotational = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())



    user_shifts = relationship("UserShift", back_populates="shift")
    shift_roster_details = relationship("ShiftRosterDetail", back_populates="shift")