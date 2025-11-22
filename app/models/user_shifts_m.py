from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey, DateTime, String, func
from sqlalchemy.orm import relationship
from app.database import Base

class UserShift(Base):
    __tablename__ = "user_shifts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    assigned_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Audit user tracking
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="user_shifts")
    shift = relationship("Shift", back_populates="user_shifts")
