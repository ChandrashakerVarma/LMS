from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PayrollAttendance(Base):
    __tablename__ = "payroll_attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String(10), nullable=False)  # Format: YYYY-MM
    total_days = Column(Integer, default=0)
    present_days = Column(Integer, default=0)
    half_days = Column(Integer, default=0)
    absent_days = Column(Integer, default=0)
    gross_salary = Column(Float, default=0.0)
    net_salary = Column(Float, default=0.0)
    status = Column(String(20), default="Generated")  # Generated / Approved / Paid
    generated_on = Column(Date)

    user = relationship("User", back_populates="payroll_attendances")
