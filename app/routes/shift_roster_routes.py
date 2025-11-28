from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.shift_roster_m import ShiftRoster
from app.Schema.shift_roster_schema import (
    ShiftRosterCreate, ShiftRosterUpdate, ShiftRosterResponse
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/shift_rosters", tags=["Shift Rosters"])


# ---------------------- CREATE ----------------------
@router.post("/", response_model=ShiftRosterResponse)
def create_shift_roster(
    data: ShiftRosterCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing = db.query(ShiftRoster).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Shift Roster already exists")

    new_roster = ShiftRoster(
        **data.dict(exclude_unset=True),
        created_by=current_user.first_name
    )

    db.add(new_roster)
    db.commit()
    db.refresh(new_roster)
    return new_roster


# ---------------------- GET ALL ----------------------
@router.get("/", response_model=List[ShiftRosterResponse])
def get_all_shift_rosters(db: Session = Depends(get_db)):
    return db.query(ShiftRoster).all()


# ---------------------- GET BY ID ----------------------
@router.get("/{roster_id}", response_model=ShiftRosterResponse)
def get_shift_roster(roster_id: int, db: Session = Depends(get_db)):
    roster = db.query(ShiftRoster).filter_by(id=roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Shift Roster not found")
    return roster


# ---------------------- UPDATE ----------------------
@router.put("/{roster_id}", response_model=ShiftRosterResponse)
def update_shift_roster(
    roster_id: int,
    data: ShiftRosterUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    roster = db.query(ShiftRoster).filter_by(id=roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Shift Roster not found")

    update_data = data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(roster, key, value)

    roster.modified_by = current_user.first_name

    db.commit()
    db.refresh(roster)
    return roster


# ---------------------- DELETE ----------------------
@router.delete("/{roster_id}")
def delete_shift_roster(
    roster_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    roster = db.query(ShiftRoster).filter_by(id=roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Shift Roster not found")

    db.delete(roster)
    db.commit()

    return {"message": f"Shift Roster deleted successfully by {current_user.first_name}"}
