from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.QuizHistory_m import QuizHistory
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.schema.quiz_history_schema import QuizHistoryMessageResponse
from app.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/quiz-history", tags=["quiz_history"])


# Record quiz completion
@router.post("/{checkpoint_id}/complete", response_model=QuizHistoryMessageResponse, status_code=status.HTTP_201_CREATED)
def complete_quiz(checkpoint_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    # Create QuizHistory record
    new_history = QuizHistory(
        user_id=current_user.id,
        checkpoint_id=checkpoint.id
    )

    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    # Return using Pydantic model
    return QuizHistoryMessageResponse(
        message="Quiz completed successfully",
        id=new_history.id,
        user_id=new_history.user_id,
        checkpoint_id=new_history.checkpoint_id,
        score=new_history.score,
        completed_at=new_history.completed_at
    )

# Get quiz history for a user
@router.get("/user/{user_id}", response_model=List[QuizHistoryMessageResponse])
def get_user_quiz_history(user_id: int, db: Session = Depends(get_db)):
    histories = db.query(QuizHistory).filter(QuizHistory.user_id == user_id).all()
    if not histories:
        raise HTTPException(status_code=404, detail="No quiz history found for this user")

    # Convert to response model
    return [
        QuizHistoryMessageResponse(
            message="Fetched successfully",
            id=h.id,
            user_id=h.user_id,
            checkpoint_id=h.checkpoint_id,
            score=h.score,
            completed_at=h.completed_at
        ) for h in histories
    ]
