from sqlalchemy.orm import Session
from app.models.test_report_m import TestReport

def save_test_report(db: Session, data):
    report = TestReport(**data)
    db.add(report)
    db.commit()