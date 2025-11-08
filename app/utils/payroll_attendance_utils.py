from datetime import datetime
from sqlalchemy.orm import Session
from app.models.attendance_m import Attendance
from app.models.salary_structure_m import SalaryStructure
from app.utils.formula_engine import calculate_salary_with_formulas

def generate_attendance_based_salary(db: Session, user_id: int, month: str):
    """
    Calculates salary automatically based on attendance.
    Month format: 'YYYY-MM'
    """

    attendances = db.query(Attendance).filter(
        Attendance.user_id == user_id,
        Attendance.punch_in.like(f"{month}%")
    ).all()

    if not attendances:
        return None

    salary_structure = db.query(SalaryStructure).filter(
        SalaryStructure.user_id == user_id,
        SalaryStructure.is_active == True
    ).first()

    if not salary_structure:
        return None

    # Monthly gross from annual
    basic = (salary_structure.basic_salary_annual or 0) / 12
    allowances = (salary_structure.allowances_annual or 0) / 12
    deductions = (salary_structure.deductions_annual or 0) / 12
    bonus = (salary_structure.bonus_annual or 0) / 12

    gross_salary = basic + allowances + bonus - deductions

    # Apply formulas dynamically
    calculated = calculate_salary_with_formulas(db, gross_salary)
    gross_salary = sum(calculated.values()) if calculated else gross_salary

    # Count attendance stats
    total_days = len(attendances)
    present_days = sum(1 for a in attendances if a.status == "Full Day")
    half_days = sum(1 for a in attendances if a.status == "Half Day")
    absent_days = total_days - (present_days + half_days)

    total_working_days = 30
    per_day_salary = gross_salary / total_working_days
    payable_days = present_days + (half_days * 0.5)
    payable_salary = per_day_salary * payable_days
    net_salary = round(payable_salary - deductions, 2)

    return {
        "user_id": user_id,
        "month": month,
        "total_days": total_days,
        "present_days": present_days,
        "half_days": half_days,
        "absent_days": absent_days,
        "gross_salary": round(gross_salary, 2),
        "net_salary": net_salary,
        "generated_on": datetime.now().date(),
    }
