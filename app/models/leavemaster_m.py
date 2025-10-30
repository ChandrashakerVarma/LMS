from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class LeaveMaster(Base):
    __tablename__ = "leave_master"

    id = Column(Integer, primary_key=True, index=True)
    holiday = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    allocated = Column(Integer, default=0)
    used = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    carry_forward = Column(Boolean, default=False)
    leave_type = Column(String(50), nullable=False)  # e.g. "Sick Leave", "Casual Leave"
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = relationship("User", back_populates="leaves")
