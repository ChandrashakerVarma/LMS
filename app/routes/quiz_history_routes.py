from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.QuizHistory_m import QuizHistory
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.models.video_m import Video
<<<<<<< HEAD
from app.schema.quiz_history_schema import QuizHistoryMessageResponse
=======
from app.schema.quiz_history_schema import QuizHistoryCreate, QuizHistoryMessageResponse, QuizHistoryResponse
>>>>>>> origin/main
from app.dependencies import get_current_user

router = APIRouter(prefix="/quiz-history", tags=["quiz_history"])

<<<<<<< HEAD

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
=======
# ---------------- CREATE ----------------
@router.post("/", response_model=QuizHistoryMessageResponse, status_code=status.HTTP_201_CREATED)
def create_quiz_history(data: QuizHistoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
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
        video_id=data.video_id,  # ✅ video link
        answer=data.answer,
        result=data.result,
        question=data.question,
    )

>>>>>>> origin/main
    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    return QuizHistoryMessageResponse(
<<<<<<< HEAD
        message="Quiz completed successfully",
=======
        message="Quiz history created successfully",
>>>>>>> origin/main
        id=new_history.id,
        user_id=new_history.user_id,
        checkpoint_id=new_history.checkpoint_id,
        course_id=new_history.course_id,
        video_id=new_history.video_id,
<<<<<<< HEAD
        completed_at=new_history.completed_at
    )


# ✅ Read (Get quiz history for a user)
@router.get("/user/{user_id}", response_model=List[QuizHistoryMessageResponse])
=======
        answer=new_history.answer,
        result=new_history.result,
        question=new_history.question,
        completed_at=new_history.completed_at
    )

# ---------------- READ (all) ----------------
@router.get("/", response_model=List[QuizHistoryResponse])
def get_all_quiz_histories(db: Session = Depends(get_db)):
    return db.query(QuizHistory).all()

# ---------------- READ (by user) ----------------
@router.get("/user/{user_id}", response_model=List[QuizHistoryResponse])
>>>>>>> origin/main
def get_user_quiz_history(user_id: int, db: Session = Depends(get_db)):
    histories = db.query(QuizHistory).filter(QuizHistory.user_id == user_id).all()
    if not histories:
        raise HTTPException(status_code=404, detail="No quiz history found for this user")
<<<<<<< HEAD

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
=======
    return histories

# ---------------- READ (by ID) ----------------
@router.get("/{history_id}", response_model=QuizHistoryResponse)
def get_quiz_history(history_id: int, db: Session = Depends(get_db)):
    history = db.query(QuizHistory).filter(QuizHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")
    return history

# ---------------- UPDATE ----------------
@router.put("/{history_id}", response_model=QuizHistoryMessageResponse)
def update_quiz_history(history_id: int, update_data: QuizHistoryCreate, db: Session = Depends(get_db)):
    history = db.query(QuizHistory).filter(QuizHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")

    # Update fields
    history.user_id = update_data.user_id
    history.checkpoint_id = update_data.checkpoint_id
    history.course_id = update_data.course_id
    history.video_id = update_data.video_id  # ✅ video
    history.answer = update_data.answer
    history.result = update_data.result
    history.question = update_data.question
>>>>>>> origin/main

    db.commit()
    db.refresh(history)

    return QuizHistoryMessageResponse(
        message="Quiz history updated successfully",
        id=history.id,
        user_id=history.user_id,
        checkpoint_id=history.checkpoint_id,
        course_id=history.course_id,
        video_id=history.video_id,
<<<<<<< HEAD
        completed_at=history.completed_at
    )


# ✅ Delete (remove a quiz history record)
@router.delete("/{history_id}", response_model=QuizHistoryMessageResponse)
def delete_quiz_history(history_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    history = db.query(QuizHistory).filter(
        QuizHistory.id == history_id,
        QuizHistory.user_id == current_user.id
    ).first()

=======
        answer=history.answer,
        result=history.result,
        question=history.question,
        completed_at=history.completed_at
    )

# ---------------- DELETE ----------------
@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz_history(history_id: int, db: Session = Depends(get_db)):
    history = db.query(QuizHistory).filter(QuizHistory.id == history_id).first()
>>>>>>> origin/main
    if not history:
        raise HTTPException(status_code=404, detail="Quiz history not found")

    db.delete(history)
    db.commit()
<<<<<<< HEAD

    return QuizHistoryMessageResponse(
        message="Quiz history deleted successfully",
        id=history.id,
        user_id=history.user_id,
        checkpoint_id=history.checkpoint_id,
        course_id=history.course_id,
        video_id=history.video_id,
        completed_at=history.completed_at
    )
=======
    return {"message": "Quiz history deleted successfully"}
>>>>>>> origin/main
