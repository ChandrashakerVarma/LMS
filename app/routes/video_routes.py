from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.video_m import Video
from app.models.course_m import Course
from app.schema.video_schema import VideoCreate, VideoResponse, VideoUpdate
from app.dependencies import get_current_user, require_org_admin

# Permission dependencies
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/videos", tags=["Videos"])

MENU_ID = 32


# ---------------- CREATE ----------------
@router.post(
    "/", 
    response_model=VideoResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_video(
    video: VideoCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(require_org_admin)
):
    course = db.query(Course).filter(Course.id == video.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_video = Video(**video.dict())
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    # Update course duration
    total_duration = db.query(func.sum(Video.duration)).filter(Video.course_id == video.course_id).scalar() or 0.0
    course.duration = total_duration
    db.commit()
    db.refresh(course)

    return VideoResponse.from_orm(
        db.query(Video).options(joinedload(Video.checkpoints)).filter(Video.id == new_video.id).first()
    )


# ---------------- LIST ----------------
@router.get(
    "/", 
    response_model=List[VideoResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).options(joinedload(Video.checkpoints)).all()
    return [VideoResponse.from_orm(v) for v in videos]


# ---------------- GET BY ID ----------------
@router.get(
    "/{video_id}", 
    response_model=VideoResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).options(joinedload(Video.checkpoints)).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse.from_orm(video)


# ---------------- UPDATE ----------------
@router.put(
    "/{video_id}", 
    response_model=VideoResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_video(
    video_id: int, 
    payload: VideoUpdate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(require_org_admin)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(video, key, value)
    db.commit()
    db.refresh(video)

    # Recalculate course duration
    course = db.query(Course).filter(Course.id == video.course_id).first()
    if course:
        total_duration = db.query(func.sum(Video.duration)).filter(Video.course_id == video.course_id).scalar() or 0.0
        course.duration = total_duration
        db.commit()
        db.refresh(course)

    return VideoResponse.from_orm(
        db.query(Video).options(joinedload(Video.checkpoints)).filter(Video.id == video.id).first()
    )


# ---------------- DELETE ----------------
@router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_video(
    video_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(require_org_admin)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    course_id = video.course_id
    db.delete(video)
    db.commit()

    # Recalculate course duration
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        total_duration = db.query(func.sum(Video.duration)).filter(Video.course_id == course_id).scalar() or 0.0
        course.duration = total_duration
        db.commit()
        db.refresh(course)

    return {"message": "Video deleted successfully"}
