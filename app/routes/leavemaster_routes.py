from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.models.user_m import User
from app.schema.leavemaster_schema import LeaveMasterCreate, LeaveMasterUpdate, LeaveMasterOut
from app.dependencies import get_current_user  # Your authentication dependency

router = APIRouter(prefix="/leaves", tags=["Leave Master"])


# ➕ Create Leave Record
@router.post("/", response_model=LeaveMasterOut)
def create_leave(
    leave: LeaveMasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if user exists
    user = db.query(User).filter(User.id == leave.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if leave already exists for the same user + holiday
    existing_leave = db.query(LeaveMaster).filter(
        LeaveMaster.user_id == leave.user_id,
        LeaveMaster.holiday == leave.holiday
    ).first()
    if existing_leave:
        return existing_leave  # Return existing record

    new_leave = LeaveMaster(
        **leave.dict(),
        created_by=current_user.first_name  # Only set created_by
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave


# 📋 Get All Leaves
@router.get("/", response_model=List[LeaveMasterOut])
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leaves = db.query(LeaveMaster).all()
    return leaves


# 🔍 Get Leave by ID
@router.get("/{leave_id}", response_model=LeaveMasterOut)
def get_leave_by_id(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave record not found")
    return leave


# ✏️ Update Leave Record
@router.put("/{leave_id}", response_model=LeaveMasterOut)
def update_leave(
    leave_id: int,
    updated_data: LeaveMasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave record not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(leave, key, value)

    leave.modified_by = current_user.first_name  # Only set modified_by
    leave.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(leave)
    return leave


# ❌ Delete Leave Record
@router.delete("/{leave_id}")
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave record not found")
    db.delete(leave)
    db.commit()
    return {"message": "Leave record deleted successfully"}
