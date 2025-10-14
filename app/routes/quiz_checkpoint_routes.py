from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video_m import Video
from app.models.course_m import Course  # ✅ import Course
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.schema.quiz_checkpoint_schema import QuizCheckpointResponse, QuizCheckpointCreate, QuizCheckpointUpdate
from app.dependencies import require_admin
from typing import List

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])

# Helper function to validate timestamp
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

# Create checkpoint
@router.post("/", response_model=QuizCheckpointResponse, status_code=status.HTTP_201_CREATED)
def create_checkpoint(checkpoint: QuizCheckpointCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    validate_checkpoint_timestamp(db, checkpoint.course_id, checkpoint.video_id, checkpoint.timestamp)
    new_checkpoint = QuizCheckpoint(**checkpoint.dict())
    db.add(new_checkpoint)
    db.commit()
    db.refresh(new_checkpoint)
    return new_checkpoint

# List checkpoints
@router.get("/", response_model=List[QuizCheckpointResponse])
def list_checkpoints(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return db.query(QuizCheckpoint).all()

# Get checkpoint by ID
@router.get("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def get_checkpoint(checkpoint_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

# Update checkpoint
@router.put("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def update_checkpoint(checkpoint_id: int, updated_data: QuizCheckpointUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
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
    return checkpoint

# Delete checkpoint
@router.delete("/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkpoint(checkpoint_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    db.delete(checkpoint)
    db.commit()
    return {"message": "Checkpoint deleted successfully"}
