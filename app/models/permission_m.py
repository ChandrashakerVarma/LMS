# app/models/permission_m.py
from sqlalchemy import Column, Integer, Time, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")  # pending / approved / cancelled
    reason = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="permissions")
    shift = relationship("Shift", back_populates="permissions", lazy="joined")
