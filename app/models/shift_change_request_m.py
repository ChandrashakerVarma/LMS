from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
# ---------- STATUS ENUM ----------
class RequestStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

class ShiftChangeRequest(Base):
    __tablename__ = "shift_change_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    new_shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    request_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(String(20), default="Pending")  # Approved / Rejected / Pending

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
   
    # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    user = relationship("User", back_populates="shift_change_requests")
    
    old_shift = relationship("Shift", foreign_keys=[old_shift_id])
    new_shift = relationship("Shift", foreign_keys=[new_shift_id])
