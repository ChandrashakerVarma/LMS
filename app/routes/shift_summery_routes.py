from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db

from app.models.user_m import User
from app.models.shift_roster_m import ShiftRoster
from app.models.shift_roster_detail_m import ShiftRosterDetail
from app.models.user_shifts_m import UserShift

router = APIRouter(prefix="/monthly_shift_roster", tags=["Monthly Shift Roster"])


# --------------------------------------------------
# 1️⃣ GENERATE MONTHLY SHIFT ROSTER
# --------------------------------------------------
@router.post("/generate/{user_id}/{month}/{year}")
def generate_monthly_shift_roster(user_id: int, month: int, year: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found")

    if not user.shift_roster_id:
        raise HTTPException(400, detail="User does not have a shift roster assigned")

    roster_details = (
        db.query(ShiftRosterDetail)
        .filter(ShiftRosterDetail.shift_roster_id == user.shift_roster_id)
        .all()
    )

    if not roster_details:
        raise HTTPException(404, detail="No shift weekly pattern found for this roster")

    # Convert weekly roster details to map → weekday_id => shift_id
    weekly_map = {rd.week_day_id: rd.shift_id for rd in roster_details}

    # Calculate month boundaries
    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)

    current_date = start_date
    delta = timedelta(days=1)

    inserted = 0
    skipped = 0

    while current_date < end_date:
        weekday_id = current_date.weekday() + 1
        shift_id = weekly_map.get(weekday_id)

        if shift_id:
            existing = db.query(UserShift).filter(
                UserShift.user_id == user_id,
                UserShift.assigned_date == current_date
            ).first()

            if not existing:
                new_shift = UserShift(
                    user_id=user_id,
                    shift_id=shift_id,
                    assigned_date=current_date,
                    is_active=True
                )
                db.add(new_shift)
                inserted += 1
            else:
                skipped += 1

        current_date += delta

    db.commit()

    return {
        "message": "Monthly shift roster generated successfully.",
        "user_id": user_id,
        "month": month,
        "year": year,
        "inserted": inserted,
        "skipped": skipped
    }


# --------------------------------------------------
# 2️⃣ GET MONTHLY SHIFT ROSTER FOR A USER
# --------------------------------------------------
@router.get("/{user_id}/{month}/{year}")
def get_monthly_roster(user_id: int, month: int, year: int, db: Session = Depends(get_db)):

    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)

    shifts = db.query(UserShift).filter(
        UserShift.user_id == user_id,
        UserShift.assigned_date >= start_date,
        UserShift.assigned_date < end_date
    ).all()

    return {
        "user_id": user_id,
        "month": month,
        "year": year,
        "total_records": len(shifts),
        "shifts": shifts
    }


# --------------------------------------------------
# 3️⃣ GET SHIFT FOR A SPECIFIC DATE
# --------------------------------------------------
@router.get("/day/{user_id}/{assigned_date}")
def get_day_shift(user_id: int, assigned_date: date, db: Session = Depends(get_db)):

    shift = db.query(UserShift).filter(
        UserShift.user_id == user_id,
        UserShift.assigned_date == assigned_date
    ).first()

    if not shift:
        raise HTTPException(404, detail="Shift not found for this date")

    return shift


# --------------------------------------------------
# 4️⃣ UPDATE SHIFT FOR A SPECIFIC DATE
# --------------------------------------------------
@router.put("/update/{user_id}/{assigned_date}")
def update_day_shift(user_id: int, assigned_date: date, shift_id: int, db: Session = Depends(get_db)):

    shift = db.query(UserShift).filter(
        UserShift.user_id == user_id,
        UserShift.assigned_date == assigned_date
    ).first()

    if not shift:
        raise HTTPException(404, detail="Shift not found")

    shift.shift_id = shift_id
    db.commit()
    db.refresh(shift)

    return {"message": "Shift updated successfully", "record": shift}


# --------------------------------------------------
# 5️⃣ DELETE SHIFT FOR A SPECIFIC DATE
# --------------------------------------------------
@router.delete("/delete/{user_id}/{assigned_date}")
def delete_day_shift(user_id: int, assigned_date: date, db: Session = Depends(get_db)):

    shift = db.query(UserShift).filter(
        UserShift.user_id == user_id,
        UserShift.assigned_date == assigned_date
    ).first()

    if not shift:
        raise HTTPException(404, detail="Shift not found")

    db.delete(shift)
    db.commit()

    return {"message": "Shift deleted successfully"}


# --------------------------------------------------
# 6️⃣ DELETE ENTIRE MONTH'S ROSTER
# --------------------------------------------------
@router.delete("/delete_month/{user_id}/{month}/{year}")
def delete_month_roster(user_id: int, month: int, year: int, db: Session = Depends(get_db)):

    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)

    deleted_count = db.query(UserShift).filter(
        UserShift.user_id == user_id,
        UserShift.assigned_date >= start_date,
        UserShift.assigned_date < end_date
    ).delete()

    db.commit()

    return {
        "message": "Monthly roster deleted successfully",
        "deleted_records": deleted_count
    }
