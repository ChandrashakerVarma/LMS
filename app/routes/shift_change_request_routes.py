from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.shift_change_request_m import ShiftChangeRequest
from app.schema.shift_change_request_schema import (
    ShiftChangeRequestCreate,
    ShiftChangeRequestUpdate,
    ShiftChangeRequestOut
)

router = APIRouter(prefix="/shift-change-requests", tags=["Shift Change Requests"])


def serialize_shift_request(req: ShiftChangeRequest):
    return {
        "id": req.id,
        "user_id": req.user_id,
        "old_shift_id": req.old_shift_id,
        "new_shift_id": req.new_shift_id,
        "request_date": req.request_date,
        "reason": req.reason,
        "status": req.status
    }


@router.post("/", response_model=ShiftChangeRequestOut)
def create_request(request_data: ShiftChangeRequestCreate, db: Session = Depends(get_db)):
    req = ShiftChangeRequest(**request_data.dict())
    db.add(req)
    db.commit()
    db.refresh(req)
    return serialize_shift_request(req)


@router.get("/", response_model=List[ShiftChangeRequestOut])
def get_all_requests(db: Session = Depends(get_db)):
    items = db.query(ShiftChangeRequest).all()
    return [serialize_shift_request(i) for i in items]


@router.get("/{request_id}", response_model=ShiftChangeRequestOut)
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(ShiftChangeRequest).filter(ShiftChangeRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return serialize_shift_request(req)


@router.put("/{request_id}", response_model=ShiftChangeRequestOut)
def update_request(request_id: int, update_data: ShiftChangeRequestUpdate, db: Session = Depends(get_db)):
    req = db.query(ShiftChangeRequest).filter(ShiftChangeRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(req, key, value)

    db.commit()
    db.refresh(req)
    return serialize_shift_request(req)


@router.delete("/{request_id}")
def delete_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(ShiftChangeRequest).filter(ShiftChangeRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    db.delete(req)
    db.commit()
    return {"message": "Request deleted successfully"}
