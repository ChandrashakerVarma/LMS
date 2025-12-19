from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class TestReport(Base):
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(255), nullable=False)
    total_tests = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    failed = Column(Integer, nullable=False)
    failures = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
