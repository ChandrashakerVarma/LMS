# app/routes/leave_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.schema.leavemaster_schema import  LeaveMasterCreateBalance, LeaveMasterResponse, LeaveMasterUpdateBalance

router = APIRouter(prefix="/leaves", tags=["leaves"])

# Create Leave/Holiday
@router.post("/", response_model=LeaveMasterResponse, status_code=status.HTTP_201_CREATED)
def create_leave(leave: LeaveMasterCreateBalance, db: Session = Depends(get_db)):
    db_leave = LeaveMaster(**leave.dict())
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

# Get all Leaves/Holidays
@router.get("/", response_model=List[LeaveMasterResponse])
def get_all_leaves(db: Session = Depends(get_db)):
    return db.query(LeaveMaster).all()

# Get by ID
@router.get("/{leave_id}", response_model=LeaveMasterResponse)
def get_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return leave

# Update Leave/Holiday
@router.put("/{leave_id}", response_model=LeaveMasterResponse)
def update_leave(leave_id: int, leave_update: LeaveMasterUpdateBalance, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    for key, value in leave_update.dict(exclude_unset=True).items():
        setattr(leave, key, value)
    db.commit()
    db.refresh(leave)
    return leave

# Delete Leave/Holiday
@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    db.delete(leave)
    db.commit()
    return None
