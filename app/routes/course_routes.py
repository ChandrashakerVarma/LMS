from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course_m import Course
from app.schema.course_schema import CourseCreate, CourseResponse, CourseUpdate
from typing import List
from app.dependencies import get_current_user,require_admin

router = APIRouter(prefix="/courses", tags=["courses"])

#Create Course
@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    existing = db.query(Course).filter(Course.title == course.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course with this title already exists")

    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # ✅ Pydantic v1 way
    return CourseResponse.from_orm(new_course)


#Get course
@router.get("/", response_model=List[CourseResponse])
def list_courses(db : Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Course).all()


#Get course individual
@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


#Update Course
@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = payload.dict(exclude_unset=True)    # only update provided fields
    for key, value in update_data.items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course


#Delete Course
@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return {"message": "User deleted successfully"}
