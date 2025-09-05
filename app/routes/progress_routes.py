from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.course_m import Course
from app.models.Progress_m import Progress
from app.schema.progress_schema import ProgressResponse
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/progress", tags=["progress"])

@router.post("/{course_id}/watch", response_model=ProgressResponse, status_code=status.HTTP_200_OK)
def course_progress(course_id: int, watched_minutes: float, user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Get course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Validation: watched_minutes cannot exceed course duration
    if watched_minutes > course.duration:
        raise HTTPException(status_code=400, detail=f"Watched minutes ({watched_minutes}) cannot exceed course duration ({course.duration}).")

    # Get or create user progress
    progress = db.query(Progress).filter(
        Progress.course_id == course_id,
        Progress.user_id == user_id
    ).first()

    if not progress:
        progress = Progress(
            user_id=user_id,
            course_id=course_id,
            watched_minutes=watched_minutes
        )
        db.add(progress)
    else:
        progress.watched_minutes = watched_minutes

    # Calculate percentage (locked at 100 max)
    progress.progress_percentage = min(
        (progress.watched_minutes / course.duration) * 100,
        100.0
    )

    db.commit()
    db.refresh(progress)

    return ProgressResponse.from_orm(progress)


#Get all progress
@router.get("/", response_model= List[ProgressResponse])
def list_progress(user_id: int = None, course_id: int = None, db: Session= Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Progress)
    if user_id:
        query = query.filter(Progress.user_id == user_id)
    if course_id:
        query = query.filter(Progress.course_id == course_id)
    progress_list = query.all()
    return progress_list


#Delete a progress entry
@router.delete("/{course_id}/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_progress(course_id: int, user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    progress = db.query(Progress).filter(
        Progress.course_id == course_id,
        Progress.user_id == user_id
    ).first()
    if not Progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    db.delete(progress)
    db.commit()
    return {"message": "Progress deleted sucessfully"}
