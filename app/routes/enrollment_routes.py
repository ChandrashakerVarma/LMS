from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.enrollment_m import Enrollment
from app.models.user_m import User
from app.models.course_m import Course
from app.schema.enrollment_schema import EnrollmentCreate, EnrollmentResponse
from app.dependencies import require_admin

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

# Admin adds a user to a course
@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_user(payload: EnrollmentCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = db.query(Enrollment).filter(
        Enrollment.user_id == payload.user_id,
        Enrollment.course_id == payload.course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already enrolled in this course")

    enrollment = Enrollment(user_id=payload.user_id, course_id=payload.course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    # Convert ORM object to Pydantic model before returning
    return EnrollmentResponse.from_orm(enrollment)

# List all enrollments
@router.get("/", response_model=List[EnrollmentResponse])
def enrollments_list(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    enrollments = db.query(Enrollment).all()
    return [EnrollmentResponse.from_orm(e) for e in enrollments]

# Get enrollments by user
@router.get("/user/{user_id}", response_model=List[EnrollmentResponse])
def get_user_enrollments(user_id: int, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == user_id).all()
    return [EnrollmentResponse.from_orm(e) for e in enrollments]

# Get enrollments by course
@router.get("/course/{course_id}", response_model=List[EnrollmentResponse])
def get_course_enrollments(course_id: int, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    return [EnrollmentResponse.from_orm(e) for e in enrollments]

# Admin removes enrollment
@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enrollment)
    db.commit()
    return {"message": "Enrollment deleted successfully"}
