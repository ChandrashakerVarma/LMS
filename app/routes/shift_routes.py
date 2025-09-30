from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.shift_m import Shift
from app.schema.shift_schema import ShiftCreate, ShiftResponse, ShiftUpdate

router = APIRouter(prefix="/shifts", tags=["Shifts"])


# Create Shift
@router.post("/", response_model=ShiftResponse)
def create_shift(shift: ShiftCreate, db: Session = Depends(get_db)):
    # Check duplicate shift_code or name
    if db.query(Shift).filter(Shift.shift_code == shift.shift_code).first():
        raise HTTPException(status_code=400, detail="Shift code already exists")
    if db.query(Shift).filter(Shift.name == shift.name).first():
        raise HTTPException(status_code=400, detail="Shift name already exists")

    new_shift = Shift(**shift.dict())
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)
    return new_shift


# Get all shifts
@router.get("/", response_model=List[ShiftResponse])
def get_shifts(db: Session = Depends(get_db)):
    return db.query(Shift).all()


# Get single shift by ID
@router.get("/{shift_id}", response_model=ShiftResponse)
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


# Update shift
@router.put("/{shift_id}", response_model=ShiftResponse)
def update_shift(shift_id: int, shift_data: ShiftUpdate, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    for key, value in shift_data.dict(exclude_unset=True).items():
        setattr(shift, key, value)

    db.commit()
    db.refresh(shift)
    return shift


# Delete shift
@router.delete("/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    db.delete(shift)
    db.commit()
    return {"message": "Shift deleted successfully"}
