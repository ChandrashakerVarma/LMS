<<<<<<< HEAD
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
=======
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
>>>>>>> origin/main

class LeaveMaster(Base):
    __tablename__ = "leave_master"

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    leave_type = Column(Enum(LeaveTypeEnum), nullable=False)
    holiday = Column(Boolean, default=False)
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    leave_date = Column(Date, nullable=False)  # Keep as Date
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
=======

    # Holiday or Leave Balance
    holiday = Column(Boolean, default=False, nullable=False)  # False = Leave balance, True = Holiday

    # Common fields
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    date = Column(Date, nullable=True)  # Changed to match schema mapping

    # Leave balance fields
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # linked to user
>>>>>>> origin/main
    year = Column(Integer, nullable=True)
    allocated = Column(Integer, default=0)
    used = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    carry_forward = Column(Boolean, default=False)
<<<<<<< HEAD
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="leave_records")
=======

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship with User
    user = relationship("User", back_populates="leave_records", lazy="joined")
>>>>>>> origin/main
