# app/models/user_m.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # ======================================================
    # BASIC USER INFO
    # ======================================================
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # ======================================================
    # ORG / ROLE
    # ======================================================
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    salary_structure_id = Column(Integer, ForeignKey("salary_structures.id"), nullable=True)

    # ======================================================
    # PERSONAL / EMPLOYMENT INFO
    # ======================================================
    date_of_birth = Column(Date, nullable=True)
    joining_date = Column(Date, nullable=True)
    relieving_date = Column(Date, nullable=True)

    address = Column(String(255), nullable=True)
    designation = Column(String(100), nullable=True)
    inactive = Column(Boolean, default=False)

    biometric_id = Column(String(50), nullable=True)

    shift_roster_id = Column(Integer, ForeignKey("shift_rosters.id"), nullable=True)

    attendance_mode = Column(String(20), default="BRANCH", nullable=False)

    # ======================================================
    # SYSTEM METADATA
    # ======================================================
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    is_org_admin = Column(Boolean, default=False)

    # ======================================================
    # RELATIONSHIPS
    # ======================================================
    role = relationship("Role", back_populates="users", lazy="joined")
    branch = relationship("Branch", back_populates="users")
    organization = relationship("Organization", back_populates="users")
    department = relationship("Department", back_populates="users")

    progress = relationship("Progress", back_populates="user", lazy="selectin")

    enrollments = relationship("app.models.enrollment_m.Enrollment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    leave_records = relationship("LeaveMaster", back_populates="user",
        cascade="all, delete-orphan"
    )

    payrolls = relationship("Payroll", back_populates="user",
        cascade="all, delete-orphan"
    )

    payroll_attendances = relationship("PayrollAttendance", back_populates="user")

    attendances = relationship("Attendance", back_populates="user",
        cascade="all, delete-orphan"
    )

    permissions = relationship("Permission", back_populates="user",
        cascade="all, delete-orphan"
    )

    shift_change_requests = relationship("ShiftChangeRequest", back_populates="user",
        cascade="all, delete-orphan"
    )

    user_shifts = relationship("UserShift", back_populates="user",
        cascade="all, delete-orphan"
    )

    shift_roster = relationship("ShiftRoster", back_populates="users")

    salary_structure = relationship("SalaryStructure", back_populates="users")

    created_shifts = relationship("Shift", back_populates="created_manager")
    notifications = relationship("Notification", back_populates="user",
        cascade="all, delete-orphan"
    )

    # ❗ Commented cause no FK exists
    # job_postings = relationship("JobPosting", back_populates="created_by")

    faces = relationship("UserFace", back_populates="user", cascade="all, delete-orphan")
