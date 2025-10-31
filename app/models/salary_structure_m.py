from sqlalchemy import Column, Integer, Float, ForeignKey, Date, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Annual-based structure
    basic_salary_annual = Column(Float, nullable=False)
    allowances_annual = Column(Float, default=0.0)
    deductions_annual = Column(Float, default=0.0)
    bonus_annual = Column(Float, default=0.0)
    total_annual = Column(Float, default=0.0)

    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="salary_structure")
    payrolls = relationship("Payroll", back_populates="salary_structure")  # make sure Payroll model has this
    formulas = relationship("Formula", back_populates="salary_structure")


