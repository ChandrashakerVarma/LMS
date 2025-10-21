from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------------- Base Schema ----------------
class PayrollBase(BaseModel):
    user_id: int
    salary_structure_id: int
    month: str = Field(..., example="2025-10")  # Format: YYYY-MM


# ---------------- Create Schema ----------------
class PayrollCreate(PayrollBase):
    # HR shouldn't send salary fields — backend calculates automatically
    pass


# ---------------- Update Schema ----------------
class PayrollUpdate(BaseModel):
    status: Optional[str] = None  # For marking Paid, Approved, etc.
    recalculate: Optional[bool] = Field(
        False, description="If True, system recalculates salary using latest formulas."
    )


# ---------------- Response Schema ----------------
class PayrollResponse(BaseModel):
    id: int
    user_id: int
    salary_structure_id: int
    month: str
    basic_salary: float
    allowances: float
    deductions: float
    bonus: float
    gross_salary: float
    net_salary: float
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    user_name: Optional[str] = None
    salary_structure_name: Optional[str] = None

    class Config:
        orm_mode = True
