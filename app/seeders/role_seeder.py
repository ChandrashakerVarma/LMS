# app/seeders/seed_roles.py
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.role_m import Role

def seed_roles():
    roles = [
        {"id": 1, "name": "admin"},
        {"id": 2, "name": "user"},
        {"id": 3, "name": "manager"}
    ]

    db: Session = SessionLocal()
    for r in roles:
        existing = db.query(Role).filter_by(id=r["id"]).first()
        if not existing:
            db.add(Role(id=r["id"], name=r["name"]))
    db.commit()
    db.close()


# Optional: allow running directly
if __name__ == "__main__":
    seed_roles()