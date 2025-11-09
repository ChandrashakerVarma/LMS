from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class ShiftRoster(Base):
    __tablename__ = "shift_rosters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    # Reverse relationship
    user_shifts = relationship("UserShift", back_populates="shift_roster")
    shift_roster_details = relationship("ShiftRosterDetail", back_populates="shift_roster")