from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.shift_roaster_m import ShiftRoster
from app.schema.shift_roaster_scchema import (
    ShiftRosterCreate, ShiftRosterUpdate, ShiftRosterResponse
)

router = APIRouter(prefix="/shift_rosters", tags=["Shift Rosters"])

# Create
@router.post("/", response_model=ShiftRosterResponse)
def create_shift_roster(data: ShiftRosterCreate, db: Session = Depends(get_db)):
    existing = db.query(ShiftRoster).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Shift Roster already exists")

    new_roster = ShiftRoster(**data.dict())
    db.add(new_roster)
    db.commit()
    db.refresh(new_roster)
    return new_roster


# Get all
@router.get("/", response_model=list[ShiftRosterResponse])
def get_all_shift_rosters(db: Session = Depends(get_db)):
    return db.query(ShiftRoster).all()


# Get by ID
@router.get("/{roster_id}", response_model=ShiftRosterResponse)
def get_shift_roster(roster_id: int, db: Session = Depends(get_db)):
    roster = db.query(ShiftRoster).filter_by(id=roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Shift Roster not found")
    return roster


# Update
@router.put("/{roster_id}", response_model=ShiftRosterResponse)
def update_shift_roster(roster_id: int, data: ShiftRosterUpdate, db: Session = Depends(get_db)):
    roster = db.query(ShiftRoster).filter_by(id=roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Shift Roster not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(roster, key, value)

    db.commit()
    db.refresh(roster)
    return roster


# Delete
@router.delete("/{roster_id}")
def delete_shift_roster(roster_id: int, db: Session = Depends(get_db)):
    roster = db.query(ShiftRoster).filter_by(id=roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Shift Roster not found")

    db.delete(roster)
    db.commit()
    return {"message": "Shift Roster deleted successfully"}
