from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.shift_m import Shift
from app.schema.shift_schema import ShiftCreate, ShiftUpdate, ShiftOut

router = APIRouter(prefix="/shifts", tags=["Shifts"])

# ➕ Create Shift
@router.post("/", response_model=ShiftOut)
def create_shift(shift: ShiftCreate, db: Session = Depends(get_db)):
    existing_shift = db.query(Shift).filter(Shift.shift_code == shift.shift_code).first()
    if existing_shift:
        raise HTTPException(status_code=400, detail="Shift code already exists")
    
    new_shift = Shift(**shift.dict())
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)
    return new_shift

# 📋 Get All Shifts
@router.get("/", response_model=List[ShiftOut])
def get_all_shifts(db: Session = Depends(get_db)):
    return db.query(Shift).all()

# 🔍 Get Shift by ID
@router.get("/{shift_id}", response_model=ShiftOut)
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift

# ✏️ Update Shift
@router.put("/{shift_id}", response_model=ShiftOut)
def update_shift(shift_id: int, updated_data: ShiftUpdate, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(shift, key, value)
    db.commit()
    db.refresh(shift)
    return shift

# ❌ Delete Shift
@router.delete("/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    db.delete(shift)
    db.commit()
    return {"message": "Shift deleted successfully"}
