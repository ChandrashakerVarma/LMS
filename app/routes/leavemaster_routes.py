# app/routes/leave_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.schema.leavemaster_schema import LeaveMasterCreate, LeaveMasterResponse, LeaveMasterUpdate

router = APIRouter(prefix="/leaves", tags=["Leaves"])


# ---------------- Create Leave / Holiday ----------------
@router.post("/", response_model=LeaveMasterResponse, status_code=status.HTTP_201_CREATED)
def create_leave(leave: LeaveMasterCreate, db: Session = Depends(get_db)):
    # Ensure dict keys match SQLAlchemy model column names
    leave_data = leave.dict()
    if "leave_date" in leave_data:
        leave_data["date"] = leave_data.pop("leave_date")  # map to model's "date" column

    db_leave = LeaveMaster(**leave_data)
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave


# ---------------- Get All Leaves ----------------
@router.get("/", response_model=List[LeaveMasterResponse])
def get_all_leaves(db: Session = Depends(get_db)):
    leaves = db.query(LeaveMaster).all()
    return leaves


# ---------------- Get Leave by ID ----------------
@router.get("/{leave_id}", response_model=LeaveMasterResponse)
def get_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave/Holiday not found")
    return leave


# ---------------- Update Leave by ID ----------------
@router.put("/{leave_id}", response_model=LeaveMasterResponse)
def update_leave(leave_id: int, update_data: LeaveMasterUpdate, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave/Holiday not found")

    update_dict = update_data.dict(exclude_unset=True)
    if "leave_date" in update_dict:
        update_dict["date"] = update_dict.pop("leave_date")  # map to model's "date" column

    for key, value in update_dict.items():
        setattr(leave, key, value)

    db.commit()
    db.refresh(leave)
    return leave


# ---------------- Delete Leave by ID ----------------
@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave/Holiday not found")

    db.delete(leave)
    db.commit()
    return {"message": "Leave/Holiday deleted successfully"}
