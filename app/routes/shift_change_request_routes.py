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
from app.models.user_m import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/shift-change-requests", tags=["Shift Change Requests"])


# CREATE SHIFT CHANGE REQUEST
@router.post("/", response_model=ShiftChangeRequestOut)
def create_request(
    request_data: ShiftChangeRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ---- CHECK IF REQUEST ALREADY EXISTS ----
    existing = (
        db.query(ShiftChangeRequest)
        .filter(
            ShiftChangeRequest.user_id == current_user.id,
            ShiftChangeRequest.request_date == request_data.request_date,
            ShiftChangeRequest.new_shift_id == request_data.new_shift_id
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Shift change request already exists for this date.")

    # Remove user_id from payload (avoid duplicate)
    data = request_data.dict()
    data.pop("user_id", None)

    # ---- CREATE NEW REQUEST ----
    new_request = ShiftChangeRequest(
        **data,
        user_id=current_user.id,
        created_by=current_user.first_name,
        modified_by=current_user.first_name
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


# GET ALL
@router.get("/", response_model=List[ShiftChangeRequestOut])
def get_all_requests(db: Session = Depends(get_db)):
    return db.query(ShiftChangeRequest).all()


# GET ONE
@router.get("/{request_id}", response_model=ShiftChangeRequestOut)
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = (
        db.query(ShiftChangeRequest)
        .filter(ShiftChangeRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


# UPDATE
@router.put("/{request_id}", response_model=ShiftChangeRequestOut)
def update_request(
    request_id: int,
    update_data: ShiftChangeRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = (
        db.query(ShiftChangeRequest)
        .filter(ShiftChangeRequest.id == request_id)
        .first()
    )

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(req, key, value)

    req.modified_by = current_user.first_name

    db.commit()
    db.refresh(req)

    return req


# DELETE
@router.delete("/{request_id}")
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = (
        db.query(ShiftChangeRequest)
        .filter(ShiftChangeRequest.id == request_id)
        .first()
    )

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    db.delete(req)
    db.commit()

    return {"message": f"Shift change request deleted successfully by {current_user.first_name}"}
