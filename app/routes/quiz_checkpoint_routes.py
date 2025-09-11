from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video_m import Video  # Import the Video model
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.schema.quiz_checkpoint_schema import QuizCheckpointResponse, QuizCheckpointCreate
from app.dependencies import require_admin  # Ensure this checks for admin rights
from typing import List

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])

# Helper function to validate timestamp
def validate_checkpoint_timestamp(db: Session, video_id: int, timestamp: float):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if not (0 <= timestamp <= video.duration):
        raise HTTPException(status_code=400, detail="Checkpoint timestamp must be within video duration")
    return video

#  Create a new checkpoint (admin only)
@router.post("/", response_model=QuizCheckpointResponse, status_code=status.HTTP_201_CREATED)
def create_checkpoint(checkpoint: QuizCheckpointCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    validate_checkpoint_timestamp(db, checkpoint.video_id, checkpoint.timestamp)
    new_checkpoint = QuizCheckpoint(**checkpoint.dict())
    db.add(new_checkpoint)
    db.commit()
    db.refresh(new_checkpoint)
    return new_checkpoint

#  List all checkpoints (admin only)
@router.get("/", response_model=List[QuizCheckpointResponse])
def list_checkpoints(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return db.query(QuizCheckpoint).all()

#  Get a single checkpoint by ID (admin only)
@router.get("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def get_checkpoint(checkpoint_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

#  Update a checkpoint (admin only)
@router.put("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def update_checkpoint(checkpoint_id: int, updated_data: QuizCheckpointCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    validate_checkpoint_timestamp(db, updated_data.video_id, updated_data.timestamp)
    for key, value in updated_data.dict().items():
        setattr(checkpoint, key, value)
    db.commit()
    db.refresh(checkpoint)
    return checkpoint

#  Delete a checkpoint (admin only)
@router.delete("/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkpoint(checkpoint_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    db.delete(checkpoint)
    db.commit()
    return {"message": "Checkpoint deleted successfully"}
