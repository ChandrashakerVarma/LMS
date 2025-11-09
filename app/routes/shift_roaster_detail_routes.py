from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/shift_roster_details", tags=["Shift Roster Details"])

@router.post("/", response_model=schemas.ShiftRosterDetailResponse)
def create_shift_roster_detail(detail: schemas.ShiftRosterDetailCreate, db: Session = Depends(get_db)):
    new_detail = models.ShiftRosterDetail(**detail.dict())
    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)
    return new_detail

@router.get("/", response_model=list[schemas.ShiftRosterDetailResponse])
def get_all_shift_roster_details(db: Session = Depends(get_db)):
    return db.query(models.ShiftRosterDetail).all()
