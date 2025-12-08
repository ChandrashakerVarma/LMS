from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PayrollBase(BaseModel):
    user_id: int
    salary_structure_id: int
    month: str = Field(..., json_schema_extra={"example": "2025-10"})  # v2 compatible

class PayrollCreate(PayrollBase):
    pass

class PayrollUpdate(BaseModel):
    status: Optional[str] = None
    recalculate: Optional[bool] = Field(
        False, description="If True, system recalculates salary using latest formulas."
    )

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
    user_name: Optional[str] = None
    salary_structure_name: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = {"from_attributes": True}
