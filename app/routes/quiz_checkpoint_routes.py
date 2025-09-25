# app/routes/quiz_checkpoint_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.video_m import Video
from app.models.course_m import Course
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.schema.quiz_checkpoint_schema import QuizCheckpointResponse, QuizCheckpointCreate, QuizCheckpointUpdate
from app.dependencies import require_admin

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])

def validate_checkpoint(db: Session, video_id: int, course_id: int, timestamp: float):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not (0 <= timestamp <= video.duration):
        raise HTTPException(status_code=400, detail="Checkpoint timestamp must be within video duration")
    return video, course

# ---------------- Create
@router.post("/", response_model=QuizCheckpointResponse, status_code=status.HTTP_201_CREATED)
def create_checkpoint(checkpoint: QuizCheckpointCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    validate_checkpoint(db, checkpoint.video_id, checkpoint.course_id, checkpoint.timestamp)
    new_checkpoint = QuizCheckpoint(**checkpoint.dict())
    db.add(new_checkpoint)
    db.commit()
    db.refresh(new_checkpoint)
    return new_checkpoint

# ---------------- List all
@router.get("/", response_model=List[QuizCheckpointResponse])
def list_checkpoints(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return db.query(QuizCheckpoint).all()

# ---------------- Get by ID
@router.get("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def get_checkpoint(checkpoint_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

# ---------------- Update
@router.put("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def update_checkpoint(checkpoint_id: int, updated_data: QuizCheckpointUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    video_id = updated_data.video_id if updated_data.video_id is not None else checkpoint.video_id
    course_id = updated_data.course_id if updated_data.course_id is not None else checkpoint.course_id
    timestamp = updated_data.timestamp if updated_data.timestamp is not None else checkpoint.timestamp
    validate_checkpoint(db, video_id, course_id, timestamp)

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(checkpoint, key, value)

    db.commit()
    db.refresh(checkpoint)
    return checkpoint

# ---------------- Delete
@router.delete("/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkpoint(checkpoint_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    db.delete(checkpoint)
    db.commit()
    return {"message": "Checkpoint deleted successfully"}

# ---------------- List checkpoints by video (Optional)
@router.get("/video/{video_id}", response_model=List[QuizCheckpointResponse])
def list_checkpoints_by_video(video_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoints = db.query(QuizCheckpoint).filter(QuizCheckpoint.video_id == video_id).all()
    return checkpoints
