# app/routes/payroll_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.payroll_m import Payroll
from app.models.salary_structure_m import SalaryStructure
from app.models.formula_m import Formula  # ✅ Import formula model
from app.schema.payroll_schema import PayrollCreate, PayrollUpdate, PayrollResponse
from app.utils.formula_engine import evaluate_formula  # ✅ Import formula evaluator
from app.dependencies import require_admin

router = APIRouter(prefix="/payrolls", tags=["Payrolls"])


# 🧮 Utility Function: Formula-based salary calculation
def calculate_salary_with_formulas(db: Session, gross_salary: float) -> dict:
    """
    Apply active formulas dynamically based on GROSS.
    Example formulas: BASIC=GROSS@40%, HRA=GROSS@10%, PF=(BASIC+HRA)@12%
    """
    formulas = db.query(Formula).filter(Formula.is_active == True).all()
    context = {"GROSS": gross_salary}

    for f in formulas:
        value = evaluate_formula(f.formula_text, context)
        context[f.component_code] = value

    return context


# ---------------- CREATE ----------------
@router.post("/", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
def create_payroll(
    payload: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # 🔹 Fetch salary structure
    salary_structure = db.query(SalaryStructure).filter(
        SalaryStructure.id == payload.salary_structure_id,
        SalaryStructure.is_active == True
    ).first()

    if not salary_structure:
        raise HTTPException(status_code=404, detail="Salary structure not found or inactive")

    # 🔹 Base monthly gross from annual structure
    gross_salary = (salary_structure.basic_salary_annual +
                    salary_structure.allowances_annual +
                    salary_structure.bonus_annual -
                    salary_structure.deductions_annual) / 12

    # 🔹 Calculate formula-driven salary components
    calculated = calculate_salary_with_formulas(db, gross_salary)

    # 🔹 Extract defaults
    basic_salary = calculated.get("BASIC", salary_structure.basic_salary_annual / 12)
    allowances = calculated.get("HRA", salary_structure.allowances_annual / 12)
    deductions = calculated.get("PF", salary_structure.deductions_annual / 12)
    bonus = calculated.get("BONUS", salary_structure.bonus_annual / 12)

    # 🔹 Manual override support: if HR passes any value in payload, it overrides formula
    basic_salary = payload.basic_salary or basic_salary
    allowances = payload.allowances or allowances
    deductions = payload.deductions or deductions
    bonus = payload.bonus or bonus

    # 🔹 Final gross/net salary
    gross_salary = basic_salary + allowances + bonus
    net_salary = gross_salary - deductions

    # 🔹 Create Payroll
    new_payroll = Payroll(
        user_id=salary_structure.user_id,
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


# ---------------- READ ALL ----------------
@router.get("/", response_model=List[PayrollResponse])
def list_payrolls(db: Session = Depends(get_db)):
    return db.query(Payroll).all()


# ---------------- READ BY ID ----------------
@router.get("/{payroll_id}", response_model=PayrollResponse)
def get_payroll(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    return payroll


# ---------------- READ BY USER ----------------
@router.get("/user/{user_id}", response_model=List[PayrollResponse])
def get_user_payrolls(user_id: int, db: Session = Depends(get_db)):
    payrolls = db.query(Payroll).filter(Payroll.user_id == user_id).all()
    if not payrolls:
        raise HTTPException(status_code=404, detail="No payroll records found for this user")
    return payrolls


# ---------------- UPDATE ----------------
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

    # 🔹 Recalculate using structure if provided
    if payload.salary_structure_id:
        salary_structure = db.query(SalaryStructure).filter(
            SalaryStructure.id == payload.salary_structure_id,
            SalaryStructure.is_active == True
        ).first()
        if not salary_structure:
            raise HTTPException(status_code=404, detail="Salary structure not found or inactive")

        gross_salary = (salary_structure.basic_salary_annual +
                        salary_structure.allowances_annual +
                        salary_structure.bonus_annual -
                        salary_structure.deductions_annual) / 12

        calculated = calculate_salary_with_formulas(db, gross_salary)
        payroll.basic_salary = calculated.get("BASIC", payroll.basic_salary)
        payroll.allowances = calculated.get("HRA", payroll.allowances)
        payroll.deductions = calculated.get("PF", payroll.deductions)
        payroll.bonus = calculated.get("BONUS", payroll.bonus)

    # 🔹 Apply manual field overrides
    for key, value in payload.dict(exclude_unset=True, exclude={"salary_structure_id"}).items():
        setattr(payroll, key, value)

    # 🔹 Recalculate totals
    payroll.gross_salary = payroll.basic_salary + payroll.allowances + payroll.bonus
    payroll.net_salary = payroll.gross_salary - payroll.deductions

    db.commit()
    db.refresh(payroll)
    return payroll


# ---------------- DELETE ----------------
@router.delete("/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payroll(
    payroll_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")

    db.delete(payroll)
    db.commit()
    return {"message": "Payroll deleted successfully"}
