from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.holiday_m import Holiday
from app.schemas.holiday_schema import HolidayCreate, HolidayUpdate, HolidayResponse
from app.dependencies import get_current_user  # adjust import based on your project

router = APIRouter(prefix="/holidays", tags=["Holidays"])


# -------------------- CREATE HOLIDAY --------------------
@router.post("/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(
    payload: HolidayCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check if holiday already exists on that date
    holiday_exists = db.query(Holiday).filter(Holiday.date == payload.date).first()
    if holiday_exists:
        raise HTTPException(status_code=400, detail="Holiday already exists")

    new_holiday = Holiday(
        date=payload.date,
        name=payload.name,
        created_by=current_user.first_name 
    )

    db.add(new_holiday)
    db.commit()
    db.refresh(new_holiday)
    return new_holiday


# -------------------- GET ALL HOLIDAYS --------------------
@router.get("/", response_model=list[HolidayResponse])
def get_holidays(db: Session = Depends(get_db)):
    return db.query(Holiday).order_by(Holiday.date.asc()).all()


# -------------------- GET HOLIDAY BY ID --------------------
@router.get("/{holiday_id}", response_model=HolidayResponse)
def get_holiday(holiday_id: int, db: Session = Depends(get_db)):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return holiday


# -------------------- UPDATE HOLIDAY --------------------
@router.put("/{holiday_id}", response_model=HolidayResponse)
def update_holiday(
    holiday_id: int,
    payload: HolidayUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    if payload.date:
        holiday.date = payload.date

    if payload.name:
        holiday.name = payload.name

    holiday.modified_by = current_user.first_name  # 👈 ADDED

    db.commit()
    db.refresh(holiday)
    return holiday


# -------------------- DELETE HOLIDAY --------------------
@router.delete("/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    db.delete(holiday)
    db.commit()
    return {"message": "Holiday deleted successfully"}
