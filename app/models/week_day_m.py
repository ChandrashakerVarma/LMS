from sqlalchemy import Column, Integer, String, Boolean, func,DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class WeekDay(Base):
    __tablename__ = "week_days"

    id = Column(Integer, primary_key=True, index=True)
    week_name = Column(String(20), nullable=False, unique=True)  # e.g., Monday
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # ✅ Correct reference
    shift_roster_details = relationship("ShiftRosterDetail", back_populates="week_day")
