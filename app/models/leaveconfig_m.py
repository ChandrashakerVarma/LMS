from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveConfig(Base):
    __tablename__ = "leave_config"

    id = Column(Integer, primary_key=True, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)

    per_month = Column(Integer, nullable=False)
    no_of_leaves = Column(Integer, nullable=False)
    carry_forward = Column(Boolean, default=False)   # TRUE / FALSE

    # ---------- AUDIT FIELDS ----------
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationship
    leave_type = relationship("LeaveType")
