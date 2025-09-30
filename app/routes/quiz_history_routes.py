from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.QuizHistory_m import QuizHistory
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.models.video_m import Video
from app.schema.quiz_history_schema import QuizHistoryMessageResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/quiz-history", tags=["quiz_history"])


# ✅ Create (Record quiz completion)
@router.post("/{checkpoint_id}/complete/{video_id}", response_model=QuizHistoryMessageResponse, status_code=status.HTTP_201_CREATED)
def complete_quiz(
    checkpoint_id: int,
    video_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    new_history = QuizHistory(
        user_id=current_user.id,
        checkpoint_id=checkpoint.id,
        video_id=video.id,
        course_id=checkpoint.course_id  # ✅ automatically link course via checkpoint
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    return QuizHistoryMessageResponse(
        message="Quiz completed successfully",
        id=new_history.id,
        user_id=new_history.user_id,
        checkpoint_id=new_history.checkpoint_id,
        course_id=new_history.course_id,
        video_id=new_history.video_id,
        completed_at=new_history.completed_at
    )


# ✅ Read (Get quiz history for a user)
@router.get("/user/{user_id}", response_model=List[QuizHistoryMessageResponse])
def get_user_quiz_history(user_id: int, db: Session = Depends(get_db)):
    histories = db.query(QuizHistory).filter(QuizHistory.user_id == user_id).all()
    if not histories:
        raise HTTPException(status_code=404, detail="No quiz history found for this user")

    return [
        QuizHistoryMessageResponse(
            message="Fetched successfully",
            id=h.id,
            user_id=h.user_id,
            checkpoint_id=h.checkpoint_id,
            course_id=h.course_id,
            video_id=h.video_id,
            completed_at=h.completed_at
        ) for h in histories
    ]


# ✅ Update (change checkpoint or video if needed)
@router.put("/{history_id}", response_model=QuizHistoryMessageResponse)
def update_quiz_history(
    history_id: int,
    checkpoint_id: int,
    video_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    history = db.query(QuizHistory).filter(
        QuizHistory.id == history_id,
        QuizHistory.user_id == current_user.id
    ).first()

    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")

    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    history.checkpoint_id = checkpoint.id
    history.video_id = video.id
    history.course_id = checkpoint.course_id

    db.commit()
    db.refresh(history)

    return QuizHistoryMessageResponse(
        message="Quiz history updated successfully",
        id=history.id,
        user_id=history.user_id,
        checkpoint_id=history.checkpoint_id,
        course_id=history.course_id,
        video_id=history.video_id,
        completed_at=history.completed_at
    )


# ✅ Delete (remove a quiz history record)
@router.delete("/{history_id}", response_model=QuizHistoryMessageResponse)
def delete_quiz_history(history_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    history = db.query(QuizHistory).filter(
        QuizHistory.id == history_id,
        QuizHistory.user_id == current_user.id
    ).first()

    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")

    db.delete(history)
    db.commit()

    return QuizHistoryMessageResponse(
        message="Quiz history deleted successfully",
        id=history.id,
        user_id=history.user_id,
        checkpoint_id=history.checkpoint_id,
        course_id=history.course_id,
        video_id=history.video_id,
        completed_at=history.completed_at
    )
