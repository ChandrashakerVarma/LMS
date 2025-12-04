from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.QuizHistory_m import QuizHistory
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.models.video_m import Video
from app.schemas.quiz_history_schema import QuizHistoryCreate, QuizHistoryMessageResponse, QuizHistoryResponse
from app.dependencies import get_current_user

# ✅ Permission imports
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/quiz-history", tags=["quiz_history"])

MENU_ID = 36

# ---------------- CREATE ----------------
@router.post(
    "/", 
    response_model=QuizHistoryMessageResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_quiz_history(
    data: QuizHistoryCreate, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    # Validate checkpoint
    checkpoint = db.query(QuizCheckpoint).filter(QuizCheckpoint.id == data.checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    # Validate video
    video = db.query(Video).filter(Video.id == data.video_id, Video.id == checkpoint.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or does not match checkpoint")

    new_history = QuizHistory(
        user_id=data.user_id,
        checkpoint_id=data.checkpoint_id,
        course_id=data.course_id,
        video_id=data.video_id,
        answer=data.answer,
        result=data.result,
        question=data.question,
    )

    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    return QuizHistoryMessageResponse(
        message="Quiz history created successfully",
        id=new_history.id,
        user_id=new_history.user_id,
        checkpoint_id=new_history.checkpoint_id,
        course_id=new_history.course_id,
        video_id=new_history.video_id,
        answer=new_history.answer,
        result=new_history.result,
        question=new_history.question,
        completed_at=new_history.completed_at
    )

# ---------------- READ (all) ----------------
@router.get(
    "/", 
    response_model=List[QuizHistoryResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_quiz_histories(db: Session = Depends(get_db)):
    return db.query(QuizHistory).all()

# ---------------- READ (by user) ----------------
@router.get(
    "/user/{user_id}", 
    response_model=List[QuizHistoryResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_user_quiz_history(user_id: int, db: Session = Depends(get_db)):
    histories = db.query(QuizHistory).filter(QuizHistory.user_id == user_id).all()
    if not histories:
        raise HTTPException(status_code=404, detail="No quiz history found for this user")
    return histories

# ---------------- READ (by ID) ----------------
@router.get(
    "/{history_id}", 
    response_model=QuizHistoryResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_quiz_history(history_id: int, db: Session = Depends(get_db)):
    history = db.query(QuizHistory).filter(QuizHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")
    return history

# ---------------- UPDATE ----------------
@router.put(
    "/{history_id}", 
    response_model=QuizHistoryMessageResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_quiz_history(history_id: int, update_data: QuizHistoryCreate, db: Session = Depends(get_db)):
    history = db.query(QuizHistory).filter(QuizHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")

    history.user_id = update_data.user_id
    history.checkpoint_id = update_data.checkpoint_id
    history.course_id = update_data.course_id
    history.video_id = update_data.video_id
    history.answer = update_data.answer
    history.result = update_data.result
    history.question = update_data.question

    db.commit()
    db.refresh(history)

    return QuizHistoryMessageResponse(
        message="Quiz history updated successfully",
        id=history.id,
        user_id=history.user_id,
        checkpoint_id=history.checkpoint_id,
        course_id=history.course_id,
        video_id=history.video_id,
        answer=history.answer,
        result=history.result,
        question=history.question,
        completed_at=history.completed_at
    )

# ---------------- DELETE ----------------
@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_quiz_history(history_id: int, db: Session = Depends(get_db)):
    history = db.query(QuizHistory).filter(QuizHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")

    db.delete(history)
    db.commit()
    return {"message": "Quiz history deleted successfully"}
