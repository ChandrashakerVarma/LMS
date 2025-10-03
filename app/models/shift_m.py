# app/models/shift_m.py
from sqlalchemy import Column, DateTime, Integer, String, Time, func
from app.database import Base

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    description = Column(String(255), nullable=True)

    shift_code = Column(String(50), unique=True, nullable=False)   # e.g., MORN, NIGHT
    shift_name = Column(String(100), nullable=False)               # e.g., Morning Shift
    working_minutes = Column(Integer, nullable=False)              # total expected working minutes
    status = Column(String(20), default="active")                  # active / inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())