# app/routes/course_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.course_m import Course
from app.schemas.course_schema import CourseCreate, CourseResponse, CourseUpdate

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/courses", tags=["courses"])

MENU_ID = 31   # Course Module ID


# ----------------------
# Create Course
# ----------------------
@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_create_permission(MENU_ID))
):
    existing = db.query(Course).filter(Course.title == course.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course with this title already exists")

    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return CourseResponse.from_orm(new_course)


# ----------------------
# List Courses (Read)
# ----------------------
@router.get("/", response_model=List[CourseResponse])
def list_courses(
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    return db.query(Course).all()


# ----------------------
# Get Single Course (Read)
# ----------------------
@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


# ----------------------
# Update Course
# ----------------------
@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_edit_permission(MENU_ID))
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = payload.dict(exclude_unset=True)

    for key, value in update_data.items():
        if key != "duration":  # prevent direct editing of duration
            setattr(course, key, value)

    db.commit()
    db.refresh(course)

    return course


# ----------------------
# Delete Course
# ----------------------
@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_delete_permission(MENU_ID))
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()

    return {"message": "Course deleted successfully"}
