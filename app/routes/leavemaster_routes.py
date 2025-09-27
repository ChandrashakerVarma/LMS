from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.schema.leavemaster_schema import LeaveMasterCreate, LeaveMasterResponse, LeaveMasterUpdate

router = APIRouter(prefix="/leaves", tags=["leaves"])

# CREATE leave
@router.post("/", response_model=LeaveMasterResponse, status_code=status.HTTP_201_CREATED)
def create_leave(leave: LeaveMasterCreate, db: Session = Depends(get_db)):
    db_leave = LeaveMaster(**leave.dict())
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

# GET all leaves
@router.get("/", response_model=List[LeaveMasterResponse])
def get_leaves(db: Session = Depends(get_db)):
    leaves = db.query(LeaveMaster).all()
    return leaves

# GET leave by ID
@router.get("/{leave_id}", response_model=LeaveMasterResponse)
def get_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return leave

# UPDATE leave
@router.put("/{leave_id}", response_model=LeaveMasterResponse)
def update_leave(leave_id: int, leave_update: LeaveMasterUpdate, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    for key, value in leave_update.dict(exclude_unset=True).items():
        setattr(leave, key, value)
    db.commit()
    db.refresh(leave)
    return leave

# DELETE leave
@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    db.delete(leave)
    db.commit()
    return None
