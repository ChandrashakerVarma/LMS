from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class LeaveMaster(Base):
    __tablename__ = "leave_master"

    id = Column(Integer, primary_key=True, index=True)

    # Holiday or Leave Balance
    holiday = Column(Boolean, default=True)  # True = Holiday, False = Leave balance

    # Common fields
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Boolean, default=True)

    # Holiday fields
    date = Column(Date, nullable=True)

    # Leave balance fields
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # linked to user
    year = Column(Integer, nullable=True)
    allocated = Column(Integer, default=0)
    used = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    carry_forward = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="leave_records")
