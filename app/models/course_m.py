<<<<<<< HEAD
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, func
=======
# app/models/course_m.py
from sqlalchemy import Column, String, Integer, Float, DateTime, func, ForeignKey
>>>>>>> origin/main
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, unique=True)
    instructor = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False, default="beginner")
<<<<<<< HEAD
    duration = Column(Float, default=0.0)
    price = Column(Float, default=0.0)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)  # ✅ add this
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)


=======
    duration = Column(Float, default=0.0)  # Total duration of all videos
    price = Column(Float, default=0.0)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)


    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)

>>>>>>> origin/main
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        server_onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="courses")
<<<<<<< HEAD
    branch = relationship("Branch", back_populates="courses")  # ✅ now works
    videos = relationship("Video", back_populates="course", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("app.models.enrollment_m.Enrollment", back_populates="course", cascade="all, delete-orphan")
    checkpoints = relationship("QuizCheckpoint", back_populates="course", cascade="all, delete-orphan")
=======
    branch = relationship("Branch", back_populates="courses")
    checkpoints = relationship("QuizCheckpoint", back_populates="course")
    videos = relationship("Video", back_populates="course", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
>>>>>>> origin/main
    category = relationship("Category", back_populates="courses")


    def __repr__(self):
        return f"<Course id={self.id} title={self.title!r} instructor={self.instructor!r}>"
