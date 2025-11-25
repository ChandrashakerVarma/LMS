from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, func
from app.database import Base

class ShiftRoster(Base):
    __tablename__ = "shift_rosters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)
    # Reverse relationship
    shift_roster_details = relationship("ShiftRosterDetail", back_populates="shift_roster")
    users = relationship("User", back_populates="shift_roster")
