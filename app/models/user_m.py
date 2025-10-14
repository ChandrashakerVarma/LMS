
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, func, LargeBinary
from sqlalchemy.orm import relationship
# app/models/user_m.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship,declarative_base
from app.database import Base
from app.models.organization import Organization


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)  # ✅ added

    # Extra fields
    date_of_birth = Column(DateTime, nullable=True)
    joining_date = Column(DateTime, nullable=True)
    relieving_date = Column(DateTime, nullable=True)
    address = Column(String(500), nullable=True)
    #photo = Column(LargeBinary, nullable=True)  # Store file path or URL

    designation = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    inactive = Column(Boolean, default=False)

    # Relationships
    role = relationship("Role", back_populates="users", lazy="joined")  # eager load by default
    progress = relationship("Progress", back_populates="user", lazy="selectin")  # selectinload for lists
    enrollments = relationship(
        "app.models.enrollment_m.Enrollment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    leave_records = relationship("LeaveMaster", back_populates="user", cascade="all, delete-orphan")
    role = relationship("Role", back_populates="users", lazy="joined")
    organization = relationship(Organization, back_populates="users")
    branch = relationship("Branch", back_populates="users")  # ✅ now works
    progress = relationship("Progress", back_populates="user", lazy="selectin")
    enrollments = relationship("Enrollment", back_populates="user")


