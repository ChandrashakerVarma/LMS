from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.models.user_m import User
from app.models.shift_roster_detail_m import ShiftRosterDetail

from app.models.user_shifts_m import UserShift
<<<<<<< HEAD
from app.dependencies import require_org_admin
=======
from app.dependencies import get_current_user
>>>>>>> origin/main

router = APIRouter(prefix="/shift-summary", tags=["Shift Summary"])


# ===============================================================
# Generate monthly shift roster
# ===============================================================
@router.post("/generate/{month}/{year}")
def generate_monthly_shift_roster(
    month: int,
    year: int,
    user_id: int | None = None,
    role_id: int | None = None,
    department_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not (user_id or role_id or department_id):
        raise HTTPException(400, detail="Provide user_id or role_id or department_id")

    query = db.query(User)

    if user_id:
        query = query.filter(User.id == user_id)
    if role_id:
        query = query.filter(User.role_id == role_id)
    if department_id:
        query = query.filter(User.department_id == department_id)

    users = query.all()
    if not users:
        raise HTTPException(404, detail="No users found for given filters")

    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)
    delta = timedelta(days=1)

    total_inserted = 0
    total_skipped = 0
    total_missing_shift_days = 0

    for user in users:

        if not user.shift_roster_id:
            print(f"User {user.id} has NO roster assigned. Skipped.")
            continue

        weekly_details = db.query(ShiftRosterDetail).filter(
            ShiftRosterDetail.shift_roster_id == user.shift_roster_id
        ).all()

        if not weekly_details:
            print(f"User {user.id} roster has NO details! Skipped.")
            continue

        # Map weekday 1–7 to shift_id
        weekly_map = {d.week_day_id: d.shift_id for d in weekly_details}

        current_date = start_date
        while current_date < end_date:

            weekday_id = current_date.weekday() + 1  # Monday=1 ... Sunday=7
            shift_id = weekly_map.get(weekday_id)

            if not shift_id:
                # No roster shift for this day
                total_missing_shift_days += 1
                current_date += delta
                continue

            # Check if assignment exists
            existing = db.query(UserShift).filter(
                UserShift.user_id == user.id,
                UserShift.assigned_date == current_date
            ).first()

            if not existing:
                db.add(
                    UserShift(
                        user_id=user.id,
                        assigned_date=current_date,
                        shift_id=shift_id,
                        created_by=current_user.first_name
                    )
                )
                total_inserted += 1
            else:
                total_skipped += 1

            current_date += delta

    db.commit()

    return {
        "message": "Monthly shift roster generated successfully",
        "month": month,
        "year": year,
        "inserted": total_inserted,
        "skipped_already_present": total_skipped,
        "days_without_roster_shift": total_missing_shift_days,
        "processed_users": len(users)
    }


# ===============================================================
# Get monthly roster summary
# ===============================================================
@router.get("/list/{month}/{year}")
def get_monthly_roster(
    month: int,
    year: int,
    user_id: int | None = None,
    role_id: int | None = None,
    department_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not (user_id or role_id or department_id):
        raise HTTPException(400, detail="Provide user_id or role_id or department_id")

    query = db.query(User)

    if user_id:
        query = query.filter(User.id == user_id)
    if role_id:
        query = query.filter(User.role_id == role_id)
    if department_id:
        query = query.filter(User.department_id == department_id)

    users = query.all()
    if not users:
        raise HTTPException(404, detail="No users found for given filters")

    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)

    response_data = []

    for user in users:

        # Fetch user's shifts
        shifts = db.query(UserShift).filter(
            UserShift.user_id == user.id,
            UserShift.assigned_date >= start_date,
            UserShift.assigned_date < end_date
        ).order_by(UserShift.assigned_date).all()

        response_data.append({
            "user_id": user.id,
            "user_name": f"{user.first_name} {user.last_name or ''}".strip(),
            "shift_count": len(shifts),
            "records": [
                {
                    "date": s.assigned_date,
                    "shift_id": s.shift_id,
                    "created_by": s.created_by,
                    "modified_by": s.modified_by,
                    "is_active": s.is_active
                }
                for s in shifts
            ]
        })

    return {
        "month": month,
        "year": year,
        "total_users": len(response_data),
        "data": response_data
    }


# ===============================================================
# Delete monthly shift roster
# ===============================================================
@router.delete("/delete/{month}/{year}")
def delete_monthly_roster(
    month: int,
    year: int,
    user_id: int | None = None,
    role_id: int | None = None,
    department_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not (user_id or role_id or department_id):
        raise HTTPException(400, detail="Provide user_id or role_id or department_id")

    query = db.query(User)

    if user_id:
        query = query.filter(User.id == user_id)
    if role_id:
        query = query.filter(User.role_id == role_id)
    if department_id:
        query = query.filter(User.department_id == department_id)

    users = query.all()
    if not users:
        raise HTTPException(404, detail="No users found")

    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)

    total_deleted = 0

    for user in users:
        deleted_count = db.query(UserShift).filter(
            UserShift.user_id == user.id,
            UserShift.assigned_date >= start_date,
            UserShift.assigned_date < end_date
        ).delete()

        total_deleted += deleted_count

    db.commit()

    return {
        "message": "Monthly roster deleted successfully",
        "month": month,
        "year": year,
<<<<<<< HEAD
        "total_deleted_records": total_deleted,
        "affected_users": len(users)
=======
        "deleted_records": total_deleted
>>>>>>> origin/main
    }
