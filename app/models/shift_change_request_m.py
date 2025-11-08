from sqlalchemy import Column, Integer, ForeignKey, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class ShiftChangeRequest(Base):
    __tablename__ = "shift_change_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    new_shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    request_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(String(20), default="Pending")  # Approved / Rejected / Pending

    user = relationship("User", back_populates="shift_change_requests")
    
    old_shift = relationship("Shift", foreign_keys=[old_shift_id])
    new_shift = relationship("Shift", foreign_keys=[new_shift_id])
