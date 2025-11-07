from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime  
from app.models.organization import Organization

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    date_of_birth = Column(DateTime, nullable=True)
    joining_date = Column(DateTime, nullable=True)
    relieving_date = Column(DateTime, nullable=True, default=None)
    
    address = Column(String(500), nullable=True)
    designation = Column(String(100), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    inactive = Column(Boolean, default=False)

    # Relationships
    role = relationship("Role", back_populates="users", lazy="joined")
    progress = relationship("Progress", back_populates="user", lazy="selectin")
    branch = relationship("Branch", back_populates="users")
    organization = relationship("Organization", back_populates="users")
    enrollments = relationship("app.models.enrollment_m.Enrollment", back_populates="user", cascade="all, delete-orphan")
    leave_records = relationship("LeaveMaster", back_populates="user", cascade="all, delete-orphan")
    salary_structure = relationship("SalaryStructure", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    payrolls = relationship("Payroll", back_populates="user", cascade="all, delete-orphan")
    payroll_attendances = relationship("PayrollAttendance", back_populates="user")
    attendances = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("Permission", back_populates="user", cascade="all, delete-orphan")

