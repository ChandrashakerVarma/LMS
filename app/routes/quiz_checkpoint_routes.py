from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.video_m import Video
from app.models.course_m import Course
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.Schema.quiz_checkpoint_schema import (
    QuizCheckpointResponse,
    QuizCheckpointCreate,
    QuizCheckpointUpdate
)

# 🔐 Permission check imports
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

MENU_ID = 35

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])


# ---------------------- Helper ----------------------
def validate_checkpoint_timestamp(db: Session, course_id: int, video_id: int, timestamp: float):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    video = db.query(Video).filter(Video.id == video_id, Video.course_id == course_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found in this course")

    if not (0 <= timestamp <= video.duration):
        raise HTTPException(status_code=400, detail="Checkpoint timestamp must be within video duration")

    return course, video


# ---------------------- CREATE ----------------------
@router.post(
    "/",
    response_model=QuizCheckpointResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(menu_id=MENU_ID))]
)
def create_checkpoint(
    checkpoint: QuizCheckpointCreate,
    db: Session = Depends(get_db)
):
    validate_checkpoint_timestamp(db, checkpoint.course_id, checkpoint.video_id, checkpoint.timestamp)
    
    new_checkpoint = QuizCheckpoint(**checkpoint.dict())
    db.add(new_checkpoint)
    db.commit()
    db.refresh(new_checkpoint)
    return QuizCheckpointResponse.from_orm(new_checkpoint)


# ---------------------- LIST ----------------------
@router.get(
    "/",
    response_model=List[QuizCheckpointResponse],
    dependencies=[Depends(require_view_permission(menu_id=MENU_ID))]
)
def list_checkpoints(
    db: Session = Depends(get_db)
):
    checkpoints = db.query(QuizCheckpoint).all()
    return [QuizCheckpointResponse.from_orm(c) for c in checkpoints]


# ---------------------- GET BY ID ----------------------
@router.get(
    "/{checkpoint_id}",
    response_model=QuizCheckpointResponse,
    dependencies=[Depends(require_view_permission(menu_id=MENU_ID))]
)
def get_checkpoint(
    checkpoint_id: int,
    db: Session = Depends(get_db)
):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    return QuizCheckpointResponse.from_orm(checkpoint)


# ---------------------- UPDATE ----------------------
@router.put(
    "/{checkpoint_id}",
    response_model=QuizCheckpointResponse,
    dependencies=[Depends(require_edit_permission(menu_id=MENU_ID))]
)
def update_checkpoint(
    checkpoint_id: int,
    updated_data: QuizCheckpointUpdate,
    db: Session = Depends(get_db)
):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    course_id = updated_data.course_id or checkpoint.course_id
    video_id = updated_data.video_id or checkpoint.video_id
    timestamp = updated_data.timestamp or checkpoint.timestamp

    validate_checkpoint_timestamp(db, course_id, video_id, timestamp)

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(checkpoint, key, value)

    db.commit()
    db.refresh(checkpoint)
    return QuizCheckpointResponse.from_orm(checkpoint)


# ---------------------- DELETE ----------------------
@router.delete(
    "/{checkpoint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(menu_id=MENU_ID))]
)
def delete_checkpoint(
    checkpoint_id: int,
    db: Session = Depends(get_db)
):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()

    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    db.delete(checkpoint)
    db.commit()

    return {"message": "Checkpoint deleted successfully"}
