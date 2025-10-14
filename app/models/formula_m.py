# app/models/formula_m.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Formula(Base):
    __tablename__ = "formulas"

    id = Column(Integer, primary_key=True, index=True)
    component_code = Column(String(50), unique=True, nullable=False)
    component_name = Column(String(100), nullable=False)
    formula_text = Column(String(255), nullable=False)  # store the actual formula here
    formula_type = Column(String(50), default="earning")  # optional: earning/deduction
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relation to salary structure (optional if you want to link formulas to a salary structure)
    salary_structure_id = Column(Integer, ForeignKey("salary_structures.id", ondelete="CASCADE"))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    salary_structure = relationship("SalaryStructure", back_populates="formulas")
