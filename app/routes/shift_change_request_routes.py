from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.shift_change_request_m import ShiftChangeRequest
from app.schema.shift_change_request_schema import (
    ShiftChangeRequestCreate,
    ShiftChangeRequestOut,
    ShiftChangeRequestUpdate,
)

router = APIRouter(prefix="/shift-change-requests", tags=["Shift Change Requests"])


# ➕ Create a new shift change request
@router.post("/", response_model=ShiftChangeRequestOut)
def create_shift_change_request(request: ShiftChangeRequestCreate, db: Session = Depends(get_db)):
    new_request = ShiftChangeRequest(**request.dict())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


# 📋 Get all shift change requests
@router.get("/", response_model=List[ShiftChangeRequestOut])
def get_all_shift_change_requests(db: Session = Depends(get_db)):
    return db.query(ShiftChangeRequest).all()


# 🔍 Get a shift change request by ID
@router.get("/{request_id}", response_model=ShiftChangeRequestOut)
def get_shift_change_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ShiftChangeRequest).filter(ShiftChangeRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Shift change request not found")
    return request


# ✏️ Update shift change request (e.g., approve/reject)
@router.put("/{request_id}", response_model=ShiftChangeRequestOut)
def update_shift_change_request(request_id: int, update_data: ShiftChangeRequestUpdate, db: Session = Depends(get_db)):
    request = db.query(ShiftChangeRequest).filter(ShiftChangeRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Shift change request not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(request, key, value)
    db.commit()
    db.refresh(request)
    return request


# ❌ Delete a shift change request
@router.delete("/{request_id}")
def delete_shift_change_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ShiftChangeRequest).filter(ShiftChangeRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Shift change request not found")

    db.delete(request)
    db.commit()
    return {"message": "Shift change request deleted successfully"}
