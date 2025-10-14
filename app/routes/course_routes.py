# app/routes/course_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.models.course_m import Course
from app.models.video_m import Video
from app.models.organization import Organization
from app.models.branch_m import Branch
from app.models.category_m import Category
from app.schema.course_schema import CourseCreate, CourseResponse, CourseUpdate
from app.dependencies import get_current_user, require_admin
from app.database import get_db  # make sure you have these

router = APIRouter(prefix="/courses", tags=["courses"])

# -----------------------
# Create a new course
# -----------------------
@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # Check for duplicate title
    existing = db.query(Course).filter(Course.title == course.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course with this title already exists")

    # Validate foreign keys
    if course.organization_id is not None:
        org = db.query(Organization).filter(Organization.id == course.organization_id).first()
        if not org:
            raise HTTPException(status_code=400, detail="Organization not found")

    if course.branch_id is not None:
        branch = db.query(Branch).filter(Branch.id == course.branch_id).first()
        if not branch:
            raise HTTPException(status_code=400, detail="Branch not found")

    if course.category_id is not None:
        cat = db.query(Category).filter(Category.id == course.category_id).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")

    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


# -----------------------
# List all courses
# -----------------------
@router.get("/", response_model=List[CourseResponse])
def list_courses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    courses = db.query(Course)\
                .options(
                    joinedload(Course.videos).joinedload(Video.checkpoints)
                ).all()
    return courses


# -----------------------
# Get a single course
# -----------------------
@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course)\
               .options(
                   joinedload(Course.videos).joinedload(Video.checkpoints)
               )\
               .filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# -----------------------
# Update course details (partial updates)
# -----------------------
@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = payload.dict(exclude_unset=True)

    # Validate foreign keys if provided
    if "organization_id" in update_data and update_data["organization_id"] is not None:
        org = db.query(Organization).filter(Organization.id == update_data["organization_id"]).first()
        if not org:
            raise HTTPException(status_code=400, detail="Organization not found")

    if "branch_id" in update_data and update_data["branch_id"] is not None:
        branch = db.query(Branch).filter(Branch.id == update_data["branch_id"]).first()
        if not branch:
            raise HTTPException(status_code=400, detail="Branch not found")

    if "category_id" in update_data and update_data["category_id"] is not None:
        cat = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")

    # Apply updates (excluding duration if needed)
    for key, value in update_data.items():
        if key != "duration":
            setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course


# -----------------------
# Delete a course
# -----------------------
@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}

