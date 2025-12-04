from sqlalchemy import Column, Integer, DateTime, String, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)

    check_in_time = Column(DateTime, nullable=True)
    check_in_lat = Column(Float, nullable=True)
    check_in_long = Column(Float, nullable=True)
    gps_score = Column(Float, nullable=True)
    location_status = Column(String(50), nullable=True)

    is_face_verified = Column(Integer, default=0)
    face_confidence = Column(Float, nullable=True)
    check_in_image_path = Column(String(255), nullable=True)

    anomaly_flag = Column(String(20), default="LOW")

    punch_out = Column(DateTime, nullable=True)
    total_worked_minutes = Column(Integer, nullable=True)
    status = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="attendances")
    shift = relationship("Shift")
