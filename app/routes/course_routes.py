# ENHANCED app/routes/course_routes.py
# ✅ Adds OPTIONAL fuzzy search to list_courses endpoint
# ✅ All existing functionality UNCHANGED

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.course_m import Course
from app.schema.course_schema import CourseCreate, CourseResponse, CourseUpdate

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/courses", tags=["courses"])

MENU_ID = 31   # Course Module ID


# ----------------------
# Create Course (UNCHANGED)
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
# ✅ ENHANCED: List Courses with OPTIONAL Fuzzy Search
# ----------------------
@router.get("/", response_model=List[CourseResponse])
def list_courses(
    # ✅ NEW: Optional fuzzy search parameters
    use_fuzzy_search: bool = Query(False, description="Enable typo-tolerant search"),
    fuzzy_query: Optional[str] = Query(None, description="Fuzzy search query"),
    fuzzy_threshold: int = Query(70, ge=50, le=100, description="Match threshold (50-100)"),
    
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    """
    List all courses with OPTIONAL fuzzy search
    
    **Default behavior (use_fuzzy_search=false):**
    - Returns all courses (unchanged)
    
    **With fuzzy search (use_fuzzy_search=true):**
    - Typo-tolerant search across: title, instructor, level
    - Results sorted by relevance
    
    **Examples:**
    - GET /courses/ → Normal (unchanged)
    - GET /courses/?use_fuzzy_search=true&fuzzy_query=python → Finds "Python", "Pyton", etc.
    - GET /courses/?use_fuzzy_search=true&fuzzy_query=john smith&fuzzy_threshold=80 → Search by instructor
    """
    
    # Build base query
    query = db.query(Course)
    
    # ✅ DECISION POINT: Use fuzzy search OR return all
    if use_fuzzy_search and fuzzy_query:
        from app.utils.fuzzy_search import apply_fuzzy_search_to_query
        
        # Define searchable fields and their importance
        search_fields = ['title', 'instructor', 'level']
        field_weights = {
            'title': 2.5,      # Most important
            'instructor': 1.5,
            'level': 1.0
        }
        
        courses = apply_fuzzy_search_to_query(
            base_query=query,
            model_class=Course,
            fuzzy_query=fuzzy_query,
            search_fields=search_fields,
            field_weights=field_weights,
            fuzzy_threshold=fuzzy_threshold
        )
        
        return courses
    else:
        # ✅ DEFAULT PATH: Return all courses (unchanged)
        return query.all()


# ----------------------
# Get Single Course (UNCHANGED)
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
# Update Course (UNCHANGED)
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
# Delete Course (UNCHANGED)
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