from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user_shifts_m import UserShift
from app.models.user_m import User
from app.models.shift_m import Shift
from app.schema.user_shifts_schema import UserShiftCreate, UserShiftUpdate, UserShiftOut

router = APIRouter(prefix="/user_shifts", tags=["User Shifts"])

# ➕ Assign Shift to User
@router.post("/", response_model=UserShiftOut)
def assign_shift(user_shift: UserShiftCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_shift.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = db.query(Shift).filter(Shift.id == user_shift.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    new_assignment = UserShift(**user_shift.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

# 📋 Get All User Shifts
@router.get("/", response_model=List[UserShiftOut])
def get_all_user_shifts(db: Session = Depends(get_db)):
    return db.query(UserShift).all()

# 🔍 Get User Shift by ID
@router.get("/{assignment_id}", response_model=UserShiftOut)
def get_user_shift(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")
    return assignment

# ✏️ Update User Shift
@router.put("/{assignment_id}", response_model=UserShiftOut)
def update_user_shift(assignment_id: int, updated_data: UserShiftUpdate, db: Session = Depends(get_db)):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(assignment, key, value)
    db.commit()
    db.refresh(assignment)
    return assignment

# ❌ Delete User Shift
@router.delete("/{assignment_id}")
def delete_user_shift(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(UserShift).filter(UserShift.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="User shift not found")
    db.delete(assignment)
    db.commit()
    return {"message": "User shift deleted successfully"}
