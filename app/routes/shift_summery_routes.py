from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.models.user_m import User
from app.models.shift_roster_detail_m import ShiftRosterDetail

from app.models.user_shifts_m import UserShift
from app.dependencies import require_org_admin

router = APIRouter(prefix="/shift-summary", tags=["Shift Summary"])


# ===============================================================
# generate monthly shift roster
# ================================================================

@router.post("/generate/{month}/{year}")
def generate_monthly_shift_roster(
    month: int,
    year: int,
    user_id: int | None = None,
    role_id: int | None = None,
    department_id: int | None = None,
    db: Session = Depends(get_db)
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

    # ---------------------------------------
    # PROCESS EACH USER
    # ---------------------------------------
    for user in users:

        if not user.shift_roster_id:
            continue  # Skip user with no roster assigned

        weekly_details = db.query(ShiftRosterDetail).filter(
            ShiftRosterDetail.shift_roster_id == user.shift_roster_id
        ).all()

        if not weekly_details:
            continue

        weekly_map = {d.week_day_id: d.shift_id for d in weekly_details}

        current_date = start_date

        while current_date < end_date:
            weekday_id = current_date.weekday() + 1
            shift_id = weekly_map.get(weekday_id)

            if shift_id:

                existing = db.query(UserShift).filter(
                    UserShift.user_id == user.id,
                    UserShift.assigned_date == current_date
                ).first()

                if not existing:
                    new_shift = UserShift(
                        user_id=user.id,
                        assigned_date=current_date,
                        shift_id=shift_id,
                        is_active=True
                    )
                    db.add(new_shift)
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
        "skipped": total_skipped,
        "processed_users": len(users)
    }

# get monthly roster summary

@router.get("/list/{month}/{year}")
def get_monthly_roster(
    month: int,
    year: int,
    user_id: int | None = None,
    role_id: int | None = None,
    department_id: int | None = None,
    db: Session = Depends(get_db)
):

    # Require at least one filter
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
        shifts = db.query(UserShift).filter(
            UserShift.user_id == user.id,
            UserShift.assigned_date >= start_date,
            UserShift.assigned_date < end_date
        ).all()

        response_data.append({
            "user_id": user.id,
            "user_name": user.first_name + " " + user.last_name if user.first_name else "",
            "shift_count": len(shifts),
            "records": [
                {
                    "assigned_date": s.assigned_date,
                    "shift_id": s.shift_id,
                    "is_active": s.is_active,
                } for s in shifts
            ]
        })

    return {
        "month": month,
        "year": year,
        "total_users": len(response_data),
        "data": response_data
    }

# =====================================================
# DELETE MONTHLY SHIFT ROSTER
# =====================================================
@router.delete("/delete/{month}/{year}")
def delete_monthly_roster(
    month: int,
    year: int,
    user_id: int | None = None,
    role_id: int | None = None,
    department_id: int | None = None,
    db: Session = Depends(get_db)
):

    # Must provide at least one filter
    if not (user_id or role_id or department_id):
        raise HTTPException(400, detail="Provide user_id or role_id or department_id")

    # Query users based on filter
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

    # Date range
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
        "total_deleted_records": total_deleted,
        "affected_users": len(users)
    }
