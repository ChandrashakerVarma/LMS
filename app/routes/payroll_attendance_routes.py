from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.payroll_attendance_m import PayrollAttendance
from app.models.attendance_summary_m import Attendance
from app.models.salary_structure_m import SalaryStructure
from app.schema.payroll_attendance_schema import (
    PayrollAttendanceBase,
    PayrollAttendanceCreate,
    PayrollAttendanceResponse,
    PayrollAttendanceUpdate,
)

# 🔹 Permission imports (as you asked)
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/payroll-attendance", tags=["Payroll - Attendance Based"])

MENU_ID = 50   # payroll_attendance menu id


# ✅ Create Payroll Attendance
@router.post(
    "/", 
    response_model=PayrollAttendanceResponse,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_payroll_attendance(user_id: int, month: str, db: Session = Depends(get_db)):
    existing = (
        db.query(PayrollAttendance)
        .filter(PayrollAttendance.user_id == user_id, PayrollAttendance.month == month)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Payroll already exists for this user and month")

    salary_structure = (
        db.query(SalaryStructure)
        .filter(SalaryStructure.is_active == True)
        .order_by(SalaryStructure.id.desc())
        .first()
    )
    if not salary_structure:
        raise HTTPException(status_code=404, detail="Salary structure not found")

    attendance_records = (
        db.query(Attendance)
        .filter(Attendance.user_id == user_id, Attendance.date.like(f"{month}%"))
        .all()
    )

    if not attendance_records:
        raise HTTPException(status_code=404, detail="Attendance records not found")

    total_days = len(attendance_records)
    present_days = sum(1 for a in attendance_records if a.status == "Present")
    half_days = sum(1 for a in attendance_records if a.status == "Half Day")
    absent_days = total_days - (present_days + half_days)

    daily_salary = salary_structure.total_annual / 12 / total_days
    gross_salary = daily_salary * (present_days + 0.5 * half_days)
    net_salary = round(gross_salary, 2)

    payroll = PayrollAttendance(
        user_id=user_id,
        month=month,
        total_days=total_days,
        present_days=present_days,
        half_days=half_days,
        absent_days=absent_days,
        gross_salary=round(gross_salary, 2),
        net_salary=net_salary,
        status="Generated",
        generated_on=datetime.now().date(),
    )

    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return payroll


# ✅ Get All Payrolls
@router.get(
    "/", 
    response_model=List[PayrollAttendanceResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_payrolls(db: Session = Depends(get_db)):
    return db.query(PayrollAttendance).all()


# ✅ Get payroll by ID
@router.get(
    "/{payroll_id}",
    response_model=PayrollAttendanceResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_payroll_by_id(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.query(PayrollAttendance).filter(PayrollAttendance.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    return payroll


# ✅ Update Payroll
@router.put(
    "/{payroll_id}",
    response_model=PayrollAttendanceResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_payroll(payroll_id: int, update_data: PayrollAttendanceUpdate, db: Session = Depends(get_db)):
    payroll = db.query(PayrollAttendance).filter(PayrollAttendance.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(payroll, field, value)

    payroll.generated_on = datetime.now().date()
    db.commit()
    db.refresh(payroll)
    return payroll


# ✅ Delete Payroll
@router.delete(
    "/{payroll_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_payroll(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.query(PayrollAttendance).filter(PayrollAttendance.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")

    db.delete(payroll)
    db.commit()
    return {"message": "Payroll record deleted successfully"}
