from sqlalchemy import DateTime, Column, Integer, ForeignKey, func, String
from sqlalchemy.orm import relationship
from app.database import Base

class ShiftRosterDetail(Base):
    __tablename__ = "shift_roster_details"

    id = Column(Integer, primary_key=True, index=True)
    shift_roster_id = Column(Integer, ForeignKey("shift_rosters.id"), nullable=False)
    week_day_id = Column(Integer, ForeignKey("week_days.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)

    # Correct timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationships
    shift_roster = relationship("ShiftRoster", back_populates="shift_roster_details")
    week_day = relationship("WeekDay", back_populates="shift_roster_details")
    shift = relationship("Shift", back_populates="shift_roster_details")
