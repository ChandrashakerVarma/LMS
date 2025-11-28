from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.payroll_m import Payroll
from app.models.user_m import User
from app.models.salary_structure_m import SalaryStructure
from app.Schema.payroll_schema import (
    PayrollCreate,
    PayrollUpdate,
    PayrollResponse
)
from app.dependencies import get_current_user

# 🚨 PERMISSIONS
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

MENU_ID = 49  # Payroll menu id

router = APIRouter(prefix="/payrolls", tags=["Payroll"])


# ------------------------------ CREATE PAYROLL ------------------------------
@router.post(
    "/", 
    response_model=PayrollResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_payroll(
    data: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate user
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Validate salary structure
    structure = db.query(SalaryStructure).filter(
        SalaryStructure.id == data.salary_structure_id
    ).first()
    if not structure:
        raise HTTPException(404, "Salary Structure not found")

    # ---- Calculate salary ----
    basic = structure.basic_salary_annual / 12
    allowances = (structure.allowances_annual or 0) / 12
    bonus = (structure.bonus_annual or 0) / 12
    deductions = (structure.deductions_annual or 0) / 12

    gross = basic + allowances + bonus
    net = gross - deductions

    payroll = Payroll(
        user_id=data.user_id,
        salary_structure_id=data.salary_structure_id,
        month=data.month,

        basic_salary=basic,
        allowances=allowances,
        bonus=bonus,
        deductions=deductions,

        gross_salary=gross,
        net_salary=net,

        created_by=current_user.first_name
    )

    db.add(payroll)
    db.commit()
    db.refresh(payroll)

    return payroll


# ------------------------------ GET ALL PAYROLLS ------------------------------
@router.get(
    "/", 
    response_model=list[PayrollResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_payrolls(db: Session = Depends(get_db)):
    data = db.query(Payroll).all()

    for p in data:
        if p.user:
            p.user_name = f"{p.user.first_name} {p.user.last_name or ''}".strip()

        if p.salary_structure:
            p.salary_structure_name = f"Structure ID {p.salary_structure.id}"

    return data


# ------------------------------ GET PAYROLL BY ID ------------------------------
@router.get(
    "/{payroll_id}", 
    response_model=PayrollResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_payroll(payroll_id: int, db: Session = Depends(get_db)):
    p = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not p:
        raise HTTPException(404, "Payroll record not found")

    if p.user:
        p.user_name = f"{p.user.first_name} {p.user.last_name or ''}".strip()

    if p.salary_structure:
        p.salary_structure_name = f"Structure ID {p.salary_structure.id}"

    return p


# ------------------------------ UPDATE PAYROLL ------------------------------
@router.put(
    "/{payroll_id}", 
    response_model=PayrollResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_payroll(
    payroll_id: int,
    data: PayrollUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(404, "Payroll not found")

    # Update status if sent
    if data.status:
        payroll.status = data.status

    # Recalculate using updated salary structure
    if data.recalculate:
        structure = payroll.salary_structure
        if structure:
            payroll.basic_salary = structure.basic_salary_annual / 12
            payroll.allowances = (structure.allowances_annual or 0) / 12
            payroll.bonus = (structure.bonus_annual or 0) / 12
            payroll.deductions = (structure.deductions_annual or 0) / 12

            payroll.gross_salary = (
                payroll.basic_salary +
                payroll.allowances +
                payroll.bonus
            )
            payroll.net_salary = payroll.gross_salary - payroll.deductions

    payroll.modified_by = current_user.first_name

    db.commit()
    db.refresh(payroll)

    if payroll.user:
        payroll.user_name = f"{payroll.user.first_name} {payroll.user.last_name or ''}".strip()

    if payroll.salary_structure:
        payroll.salary_structure_name = f"Structure ID {payroll.salary_structure.id}"

    return payroll


# ------------------------------ DELETE PAYROLL ------------------------------
@router.delete(
    "/{payroll_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_payroll(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(404, "Payroll not found")

    db.delete(payroll)
    db.commit()
    return {"message": "Payroll record deleted"}
