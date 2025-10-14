from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class LeaveTypeEnum(str, enum.Enum):
    CASUAL = "Casual Leave (CL)"
    SICK = "Sick Leave (SL)"
    EARNED = "Earned / Paid Leave (EL/PL)"
    MATERNITY = "Maternity / Paternity"
    BEREAVEMENT = "Bereavement / Compassionate"
    STUDY = "Study / Exam Leave"
    SPECIAL = "Special Leave"
    UNPAID = "Unpaid Leave"
    PUBLIC_HOLIDAY = "Public Holidays"
    COMP_OFF = "Compensatory Off"

class LeaveMaster(Base):
    __tablename__ = "leave_master"

    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(Enum(LeaveTypeEnum), nullable=False)
    holiday = Column(Boolean, default=False)
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    leave_date = Column(Date, nullable=False)  # Keep as Date
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    year = Column(Integer, nullable=True)
    allocated = Column(Integer, default=0)
    used = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    carry_forward = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="leave_records")
