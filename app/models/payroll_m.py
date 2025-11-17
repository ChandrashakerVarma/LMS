from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Payroll(Base):
    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    salary_structure_id = Column(Integer, ForeignKey("salary_structures.id", ondelete="SET NULL"), nullable=True)
    month = Column(String(7), nullable=False)  # Format: YYYY-MM

    basic_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    bonus = Column(Float, default=0.0)
    gross_salary = Column(Float, default=0.0)
    net_salary = Column(Float, default=0.0)

    status = Column(String(20), default="Pending")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="payrolls")
    salary_structure = relationship("SalaryStructure", back_populates="payrolls")
