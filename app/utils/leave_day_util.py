from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.holiday_m import Holiday


# --------------------------------------------------
# Date range helper
# --------------------------------------------------
def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


# --------------------------------------------------
# Week off rule
# ONLY Sunday is week off
# --------------------------------------------------
def is_weekoff(day: date) -> bool:
    return day.weekday() == 6  # Sunday


# --------------------------------------------------
# Calculate leave days for ONE request
# --------------------------------------------------
def calculate_leave_days(
    db: Session,
    start_date: date,
    end_date: date,
    is_half_day: bool | None
) -> float:
    """
    Calculates leave days for a single leave request
    - Excludes Sundays
    - Excludes holidays
    - Supports half-day
    """

    if not start_date or not end_date:
        return 0.0

    if is_half_day:
        return 0.5

    holidays = {
        h.date
        for h in db.query(Holiday)
        .filter(Holiday.date.between(start_date, end_date))
        .all()
    }

    total_days = 0.0

    for day in daterange(start_date, end_date):
        if is_weekoff(day):
            continue
        if day in holidays:
            continue
        total_days += 1

    return total_days
