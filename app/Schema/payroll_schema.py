from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------------- Base Schema ----------------
class PayrollBase(BaseModel):
    user_id: int
    salary_structure_id: Optional[int] = None
    month: str = Field(..., example="2025-10")  # Format: YYYY-MM
    basic_salary: float
    allowances: Optional[float] = 0.0
    deductions: Optional[float] = 0.0
    bonus: Optional[float] = 0.0
    gross_salary: Optional[float] = 0.0
    net_salary: Optional[float] = 0.0
    status: Optional[str] = "Pending"


# ---------------- Create Schema ----------------
class PayrollCreate(PayrollBase):
    pass


# ---------------- Update Schema ----------------
class PayrollUpdate(BaseModel):
    basic_salary: Optional[float] = None
    allowances: Optional[float] = None
    deductions: Optional[float] = None
    bonus: Optional[float] = None
    gross_salary: Optional[float] = None
    net_salary: Optional[float] = None
    status: Optional[str] = None


# ---------------- Response Schema ----------------
class PayrollResponse(PayrollBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    user_name: Optional[str] = None
    salary_structure_name: Optional[str] = None  # For easy display, not nested

    class Config:
        orm_mode = True
