# app/models/holiday_m.py
from sqlalchemy import Column, Integer, Date, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)

    # Holiday date (unique)
    date = Column(Date, nullable=False, unique=True, index=True)

    # Holiday name
    name = Column(String(200), nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)
