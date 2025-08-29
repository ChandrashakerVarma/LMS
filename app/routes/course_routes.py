from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course_m import Course
from app.Schema.course_s import CourseCreate, CourseResponse, CourseUpdate
from typing import List
from app.dependencies import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=CourseResponse)
def create_coutse(course: CourseCreate, db: Session = Depends(get_db)):
    existing = db.query(Course).filter(Course.title == course.title).first()
    if existing:
        raise HTTPException(status_code=400, details="course with the title already exist")

    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/", response_model=List[CourseResponse])
def list_courses(db : Session = Depends(get_db)):
    return db.query(Course).all()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), current_user: dict =Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db), user= Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return None
