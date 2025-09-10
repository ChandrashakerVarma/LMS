from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.schema.quiz_checkpoint_schema import QuizCheckpointResponse, QuizCheckpointCreate
from typing import List

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])

# ✅ Create a new checkpoint
@router.post("/", response_model=QuizCheckpointResponse, status_code=status.HTTP_201_CREATED)
def create_checkpoint(checkpoint: QuizCheckpointCreate, db: Session = Depends(get_db)):
    new_checkpoint = QuizCheckpoint(**checkpoint.dict())
    db.add(new_checkpoint)
    db.commit()
    db.refresh(new_checkpoint)
    return new_checkpoint

# ✅ List all checkpoints
@router.get("/", response_model=List[QuizCheckpointResponse])
def list_checkpoints(db: Session = Depends(get_db)):
    return db.query(QuizCheckpoint).all()

# ✅ Get a single checkpoint by ID
@router.get("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def get_checkpoint(checkpoint_id: int, db: Session = Depends(get_db)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

# ✅ Update a checkpoint
@router.put("/{checkpoint_id}", response_model=QuizCheckpointResponse)
def update_checkpoint(checkpoint_id: int, updated_data: QuizCheckpointCreate, db: Session = Depends(get_db)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    # Update fields
    for key, value in updated_data.dict().items():
        setattr(checkpoint, key, value)
    
    db.commit()
    db.refresh(checkpoint)
    return checkpoint

# ✅ Delete a checkpoint
@router.delete("/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkpoint(checkpoint_id: int, db: Session = Depends(get_db)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    db.delete(checkpoint)
    db.commit()
    return {"message": "Checkpoint deleted successfully"}
