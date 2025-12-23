from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Index, String
)
from sqlalchemy.sql import func
from app.database import Base


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)

    #  Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)

    # 📆 Tracking year
    year = Column(Integer, nullable=False)

    # Summary values
    allocated = Column(Float, nullable=False, default=0)
    used = Column(Float, nullable=False, default=0)
    pending = Column(Float, nullable=False, default=0)
    balance = Column(Float, nullable=False, default=0)

    #  Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

     # Audit
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "leave_type_id",
            "year",
            name="uq_leave_balance_user_type_year"
        ),
        Index("idx_leave_balance_user_year", "user_id", "year"),
    )
