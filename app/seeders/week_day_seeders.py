# app/seeders/seed_weekdays.py
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.week_day_m import WeekDay

def seed_weekdays():
    weekdays = [
        {"id": 1, "week_name": "Monday", "is_week_off": False},
        {"id": 2, "week_name": "Tuesday", "is_week_off": False},
        {"id": 3, "week_name": "Wednesday", "is_week_off": False},
        {"id": 4, "week_name": "Thursday", "is_week_off": False},
        {"id": 5, "week_name": "Friday", "is_week_off": False},
        {"id": 6, "week_name": "Saturday", "is_week_off": False},
        {"id": 7, "week_name": "Sunday", "is_week_off": True},
    ]
    db:Session = SessionLocal()
    for day in weekdays:
        existing = db.query(WeekDay).filter_by(week_name=day["week_name"]).first()
        if not existing:
            db.add(WeekDay(**day))

    db.commit()
    db.close()
    print("✅ Weekdays seeded successfully!")

if __name__ == "__main__":
    seed_weekdays()

