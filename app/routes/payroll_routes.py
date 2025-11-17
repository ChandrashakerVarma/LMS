from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.payroll_m import Payroll
from app.models.salary_structure_m import SalaryStructure
from app.models.formula_m import Formula
from app.schema.payroll_schema import PayrollCreate, PayrollUpdate, PayrollResponse
from app.utils.formula_engine import calculate_salary_with_formulas
from app.dependencies import require_admin

router = APIRouter(prefix="/payrolls", tags=["Payrolls"])


# 🟢 CREATE PAYROLL (Auto-calculated)
@router.post("/", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
def create_payroll(
    payload: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    salary_structure = db.query(SalaryStructure).filter(
        SalaryStructure.id == payload.salary_structure_id,
        SalaryStructure.is_active == True
    ).first()

    if not salary_structure:
        raise HTTPException(status_code=404, detail="Salary structure not found or inactive")

    # Base monthly breakdown
    basic_salary = (salary_structure.basic_salary_annual or 0) / 12
    allowances = (salary_structure.allowances_annual or 0) / 12
    deductions = (salary_structure.deductions_annual or 0) / 12
    bonus = (salary_structure.bonus_annual or 0) / 12
    gross_salary = basic_salary + allowances + bonus - deductions

    # Apply formulas dynamically
    calculated = calculate_salary_with_formulas(db, gross_salary)
    basic_salary = calculated.get("BASIC", basic_salary)
    allowances = calculated.get("HRA", allowances)
    deductions = calculated.get("PF", deductions)
    bonus = calculated.get("BONUS", bonus)

    # Final totals
    gross_salary = basic_salary + allowances + bonus
    net_salary = gross_salary - deductions

    # Save record
    new_payroll = Payroll(
        user_id=payload.user_id,
        salary_structure_id=payload.salary_structure_id,
        month=payload.month,
        basic_salary=basic_salary,
        allowances=allowances,
        deductions=deductions,
        bonus=bonus,
        gross_salary=gross_salary,
        net_salary=net_salary,
        status="Pending"
    )

    db.add(new_payroll)
    db.commit()
    db.refresh(new_payroll)
    return new_payroll


# 🟡 READ ALL PAYROLLS
@router.get("/", response_model=List[PayrollResponse])
def list_payrolls(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    payrolls = db.query(Payroll).all()
    return payrolls


# 🟡 READ SINGLE PAYROLL BY ID
@router.get("/{payroll_id}", response_model=PayrollResponse)
def get_payroll(payroll_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    return payroll


# 🟠 UPDATE PAYROLL (Status Update or Recalculate)
@router.put("/{payroll_id}", response_model=PayrollResponse)
def update_payroll(
    payroll_id: int,
    payload: PayrollUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")

    # ✅ 1. Update status if provided
    if payload.status:
        payroll.status = payload.status

    # ✅ 2. Recalculate salary if requested
    if payload.recalculate:
        salary_structure = db.query(SalaryStructure).filter(
            SalaryStructure.id == payroll.salary_structure_id,
            SalaryStructure.is_active == True
        ).first()

        if not salary_structure:
            raise HTTPException(status_code=404, detail="Salary structure not found or inactive")

        # Recalculate base monthly breakdown
        basic_salary = (salary_structure.basic_salary_annual or 0) / 12
        allowances = (salary_structure.allowances_annual or 0) / 12
        deductions = (salary_structure.deductions_annual or 0) / 12
        bonus = (salary_structure.bonus_annual or 0) / 12
        gross_salary = basic_salary + allowances + bonus - deductions

        # Apply updated formulas
        calculated = calculate_salary_with_formulas(db, gross_salary)
        basic_salary = calculated.get("BASIC", basic_salary)
        allowances = calculated.get("HRA", allowances)
        deductions = calculated.get("PF", deductions)
        bonus = calculated.get("BONUS", bonus)

        # Update payroll record
        payroll.basic_salary = basic_salary
        payroll.allowances = allowances
        payroll.deductions = deductions
        payroll.bonus = bonus
        payroll.gross_salary = basic_salary + allowances + bonus
        payroll.net_salary = payroll.gross_salary - deductions

    payroll.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(payroll)
    return payroll


# 🔴 DELETE PAYROLL
@router.delete("/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payroll(payroll_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")

    db.delete(payroll)
    db.commit()
    return {"detail": "Payroll deleted successfully"}