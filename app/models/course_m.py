from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, unique=True)
    instructor = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False, default="beginner")
    duration = Column(Float, default=0.0)
    price = Column(Float, default=0.0)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)  # ✅ add this

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        server_onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="courses")
    branch = relationship("Branch", back_populates="courses")  # ✅ now works
    videos = relationship("Video", back_populates="course", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("app.models.enrollment_m.Enrollment", back_populates="course", cascade="all, delete-orphan")
    checkpoints = relationship("QuizCheckpoint", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course id={self.id} title={self.title!r} instructor={self.instructor!r}>"
