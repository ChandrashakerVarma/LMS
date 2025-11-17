from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.payroll_attendance_m import PayrollAttendance
from app.models.attendance_m import Attendance
from app.models.salary_structure_m import SalaryStructure
from app.schema.payroll_attendance_schema import PayrollAttendanceBase, PayrollAttendanceCreate, PayrollAttendanceResponse, PayrollAttendanceUpdate
from app.utils.payroll_attendance_utils import generate_attendance_based_salary

router = APIRouter(prefix="/payroll-attendance", tags=["Payroll - Attendance Based"])


# ✅ Automatically Generate Payroll from Attendance + SalaryStructure
@router.post("/", response_model=PayrollAttendanceResponse)
def create_payroll_attendance(user_id: int, month: str, db: Session = Depends(get_db)):
    """
    Automatically generate payroll based on user's attendance and salary structure.
    """
    # --- Check for existing payroll ---
    existing = (
        db.query(PayrollAttendance)
        .filter(PayrollAttendance.user_id == user_id, PayrollAttendance.month == month)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Payroll already exists for this user and month")

    # --- Fetch salary structure ---
    salary_structure = (
        db.query(SalaryStructure)
        .filter(SalaryStructure.is_active == True)
        .order_by(SalaryStructure.id.desc())
        .first()
    )
    if not salary_structure:
        raise HTTPException(status_code=404, detail="Salary structure not found for this user")

    # --- Fetch attendance records ---
    attendance_records = (
        db.query(Attendance)
        .filter(Attendance.user_id == user_id, Attendance.date.like(f"{month}%"))
        .all()
    )
    if not attendance_records:
        raise HTTPException(status_code=404, detail="Attendance records not found for this month")

    # --- Calculate attendance summary ---
    total_days = len(attendance_records)
    present_days = sum(1 for a in attendance_records if a.status == "Present")
    half_days = sum(1 for a in attendance_records if a.status == "Half Day")
    absent_days = total_days - (present_days + half_days)

    # --- Calculate salary ---
    daily_salary = salary_structure.total_annual / 12 / total_days  # monthly days based
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
@router.get("/", response_model=List[PayrollAttendanceResponse])
def get_all_payrolls(db: Session = Depends(get_db)):
    return db.query(PayrollAttendance).all()


# ✅ Get Payroll by ID
@router.get("/{payroll_id}", response_model=PayrollAttendanceResponse)
def get_payroll_by_id(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.query(PayrollAttendance).filter(PayrollAttendance.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    return payroll


# ✅ Update Payroll (status or net salary)
@router.put("/{payroll_id}", response_model=PayrollAttendanceResponse)
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


# ✅ Delete Payroll Record
@router.delete("/{payroll_id}")
def delete_payroll(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.query(PayrollAttendance).filter(PayrollAttendance.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")

    db.delete(payroll)
    db.commit()
    return {"message": "Payroll record deleted successfully"}
