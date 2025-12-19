# app/models/leave_m.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LeaveMaster(Base):
    __tablename__ = "leave_master"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)

   # allocated = Column(Float, default=0.0)
    # used = Column(Float, default=0.0)
   # balance = Column(Float, default=0.0)

    # carry_forward = Column(Boolean, default=False)

    status = Column(String(20), default="pending")
    # pending / approved / rejected / cancelled

# 🧮 Calculated leave days for THIS request
    leave_days = Column(Float, nullable=False, default=0)

    
    # Half-day support
    is_half_day = Column(Boolean, nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Audit
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="leave_records")
    leave_type = relationship("LeaveType") 
