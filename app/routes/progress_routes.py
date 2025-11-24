from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.course_m import Course
from app.models.Progress_m import Progress
from app.schema.progress_schema import ProgressResponse
from app.dependencies import get_current_user

# 🔐 Permission checks
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

MENU_ID = 37

router = APIRouter(prefix="/progress", tags=["progress"])


# ----------------------- CREATE / UPDATE PROGRESS -----------------------
@router.post(
    "/{course_id}/watch",
    response_model=ProgressResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_create_permission(menu_id=MENU_ID))]
)
def course_progress(
    course_id: int,
    watched_minutes: float,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if watched_minutes > course.duration:
        raise HTTPException(
            status_code=400,
            detail=f"Watched minutes ({watched_minutes}) cannot exceed course duration ({course.duration})."
        )

    progress = db.query(Progress).filter(
        Progress.course_id == course_id,
        Progress.user_id == user_id
    ).first()

    if not progress:
        progress = Progress(
            user_id=user_id,
            course_id=course_id,
            watched_minutes=watched_minutes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.watched_minutes = watched_minutes
        progress.updated_at = datetime.utcnow()

    progress.progress_percentage = min(
        (progress.watched_minutes / course.duration) * 100,
        100.0
    )

    db.commit()
    db.refresh(progress)

    return ProgressResponse.from_orm(progress)


# ----------------------- GET ALL PROGRESS -----------------------
@router.get(
    "/",
    response_model=List[ProgressResponse],
    dependencies=[Depends(require_view_permission(menu_id=MENU_ID))]
)
def list_progress(
    user_id: int = None,
    course_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Progress)

    if user_id:
        query = query.filter(Progress.user_id == user_id)
    if course_id:
        query = query.filter(Progress.course_id == course_id)

    progress_list = query.all()
    return [ProgressResponse.from_orm(p) for p in progress_list]


# ----------------------- DELETE PROGRESS -----------------------
@router.delete(
    "/{course_id}/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(menu_id=MENU_ID))]
)
def delete_progress(
    course_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    progress = db.query(Progress).filter(
        Progress.course_id == course_id,
        Progress.user_id == user_id
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    db.delete(progress)
    db.commit()

    return {"message": "Progress deleted successfully"}
