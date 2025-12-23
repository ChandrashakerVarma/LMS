<<<<<<< HEAD
from sqlalchemy import JSON, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class TestReport(Base):
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)  # ✅ REQUIRED
=======
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class TestReport(Base):
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
>>>>>>> origin/main
    module_name = Column(String(255), nullable=False)
    total_tests = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    failed = Column(Integer, nullable=False)
<<<<<<< HEAD
    failures = Column(JSON, nullable=True)   # Store failures as a JSON string
=======
    failures = Column(Text, nullable=True)
>>>>>>> origin/main
    created_at = Column(DateTime(timezone=True), server_default=func.now())
