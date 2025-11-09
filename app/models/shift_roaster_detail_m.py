from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ShiftRosterDetail(Base):
    __tablename__ = "shift_roster_details"

    id = Column(Integer, primary_key=True, index=True)
    shift_roster_id = Column(Integer, ForeignKey("shift_rosters.id"), nullable=False)
    week_day_id = Column(Integer, ForeignKey("week_days.id"), nullable=False)  # ✅ FIXED here
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)

    # ✅ Correct references
    shift_roster = relationship("ShiftRoster", back_populates="shift_roster_details")
    week_day = relationship("WeekDay", back_populates="shift_roster_details")  # ✅ FIXED here
    shift = relationship("Shift", back_populates="shift_roster_details")
