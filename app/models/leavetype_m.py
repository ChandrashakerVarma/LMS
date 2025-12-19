from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(String(100), nullable=False)        # Name of the leave
    short_code = Column(String(20), nullable=False)          # Example: CL, SL, EL
    is_active = Column(Boolean, default=True)                # act/in

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)