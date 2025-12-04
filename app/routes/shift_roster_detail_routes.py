from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.shift_roster_detail_m import ShiftRosterDetail
from app.schemas.shift_roster_detail_schema import (
    ShiftRosterDetailCreate,
    ShiftRosterDetailUpdate,
    ShiftRosterDetailResponse
)

from app.database import get_db

router = APIRouter(
    prefix="/shift_roster_details",
    tags=["Shift Roster Details"]
)

# ---------------------- CREATE ----------------------
@router.post("/", response_model=ShiftRosterDetailResponse)
def create_shift_roster_detail(
    detail: ShiftRosterDetailCreate, 
    db: Session = Depends(get_db)
):

    # Duplicate check
    existing = db.query(ShiftRosterDetail).filter(
        ShiftRosterDetail.shift_roster_id == detail.shift_roster_id,
        ShiftRosterDetail.week_day_id == detail.week_day_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Shift Roster Detail already exists for this week day"
        )

    new_detail = ShiftRosterDetail(
        shift_roster_id=detail.shift_roster_id,
        week_day_id=detail.week_day_id,
        shift_id=detail.shift_id,
        created_by=detail.created_by
    )

    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)
    return new_detail


# ---------------------- GET ALL ----------------------
@router.get("/", response_model=list[ShiftRosterDetailResponse])
def get_all_shift_roster_details(db: Session = Depends(get_db)):
    return db.query(ShiftRosterDetail).all()


# ---------------------- GET BY ID ----------------------
@router.get("/{detail_id}", response_model=ShiftRosterDetailResponse)
def get_shift_roster_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = db.query(ShiftRosterDetail).filter(
        ShiftRosterDetail.id == detail_id
    ).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Shift Roster Detail not found")

    return detail


# ---------------------- UPDATE ----------------------
@router.put("/{detail_id}", response_model=ShiftRosterDetailResponse)
def update_shift_roster_detail(
    detail_id: int, 
    updated_data: ShiftRosterDetailUpdate, 
    db: Session = Depends(get_db)
):

    detail = db.query(ShiftRosterDetail).filter(
        ShiftRosterDetail.id == detail_id
    ).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Shift Roster Detail not found")

    # Duplicate check for week_day_id update
    if updated_data.week_day_id is not None:
        duplicate = db.query(ShiftRosterDetail).filter(
            ShiftRosterDetail.shift_roster_id == detail.shift_roster_id,
            ShiftRosterDetail.week_day_id == updated_data.week_day_id,
            ShiftRosterDetail.id != detail_id
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Shift Roster Detail already exists for this week day"
            )

    # Apply updates
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(detail, key, value)

    db.commit()
    db.refresh(detail)
    return detail


# ---------------------- DELETE ----------------------
@router.delete("/{detail_id}")
def delete_shift_roster_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = db.query(ShiftRosterDetail).filter(
        ShiftRosterDetail.id == detail_id
    ).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Shift Roster Detail not found")

    db.delete(detail)
    db.commit()

    return {"message": "Shift Roster Detail deleted successfully"}
