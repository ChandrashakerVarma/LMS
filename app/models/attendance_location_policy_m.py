from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey

from app.database import Base


class AttendanceLocationPolicy(Base):
    __tablename__ = "attendance_location_policies"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    mode = Column(String(20), nullable=False, default="GEO_FENCE")

    allowed_lat = Column(Float, nullable=True)
    allowed_long = Column(Float, nullable=True)
    radius_meters = Column(Integer, default=200)

    is_active = Column(Boolean, default=True)
