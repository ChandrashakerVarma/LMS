<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.schema.leavemaster_schema import LeaveCreate, LeaveOut

router = APIRouter(prefix="/leaves", tags=["Leaves"])

# 🟢 Create Leave
@router.post("/", response_model=LeaveOut)
def create_leave(leave: LeaveCreate, db: Session = Depends(get_db)):
    try:
        date_obj = datetime.strptime(leave.date, "%d-%m-%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd-mm-yyyy")

    new_leave = LeaveMaster(
        leave_type=leave.leave_type,
        name=leave.name,
        description=leave.description,
        date=date_obj,
        allocated=leave.allocated,
        used=leave.used,
        balance=leave.balance,
        carry_forward=leave.carry_forward,
        user_id=leave.user_id
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return format_leave_output(new_leave)

# 🔵 Read Leave by ID
@router.get("/{leave_id}", response_model=LeaveOut)
def get_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return format_leave_output(leave)

# 🟣 Read All Leaves
@router.get("/", response_model=List[LeaveOut])
def get_all_leaves(db: Session = Depends(get_db)):
    leaves = db.query(LeaveMaster).all()
    return [format_leave_output(leave) for leave in leaves]

# 🟠 Update Leave
@router.put("/{leave_id}", response_model=LeaveOut)
def update_leave(leave_id: int, updated_leave: LeaveCreate, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    try:
        date_obj = datetime.strptime(updated_leave.date, "%d-%m-%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd-mm-yyyy")

    leave.leave_type = updated_leave.leave_type
    leave.name = updated_leave.name
    leave.description = updated_leave.description
    leave.date = date_obj
    leave.allocated = updated_leave.allocated
    leave.used = updated_leave.used
    leave.balance = updated_leave.balance
    leave.carry_forward = updated_leave.carry_forward

    db.commit()
    db.refresh(leave)
    return format_leave_output(leave)

# 🔴 Delete Leave
@router.delete("/{leave_id}")
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    db.delete(leave)
    db.commit()
    return {"message": f"Leave ID {leave_id} deleted successfully."}

# 🧩 Helper function to format output date
def format_leave_output(leave: LeaveMaster):
    leave_out = LeaveOut.from_orm(leave)
    leave_out.date = leave.date.strftime("%d-%m-%Y")
    return leave_out
=======
# app/routes/leave_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.schema.leavemaster_schema import LeaveMasterCreate, LeaveMasterResponse, LeaveMasterUpdate

router = APIRouter(prefix="/leaves", tags=["Leaves"])


# ---------------- Create Leave / Holiday ----------------
@router.post("/", response_model=LeaveMasterResponse, status_code=status.HTTP_201_CREATED)
def create_leave(leave: LeaveMasterCreate, db: Session = Depends(get_db)):
    # Ensure dict keys match SQLAlchemy model column names
    leave_data = leave.dict()
    if "leave_date" in leave_data:
        leave_data["date"] = leave_data.pop("leave_date")  # map to model's "date" column

    db_leave = LeaveMaster(**leave_data)
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave


# ---------------- Get All Leaves ----------------
@router.get("/", response_model=List[LeaveMasterResponse])
def get_all_leaves(db: Session = Depends(get_db)):
    leaves = db.query(LeaveMaster).all()
    return leaves


# ---------------- Get Leave by ID ----------------
@router.get("/{leave_id}", response_model=LeaveMasterResponse)
def get_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave/Holiday not found")
    return leave


# ---------------- Update Leave by ID ----------------
@router.put("/{leave_id}", response_model=LeaveMasterResponse)
def update_leave(leave_id: int, update_data: LeaveMasterUpdate, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave/Holiday not found")

    update_dict = update_data.dict(exclude_unset=True)
    if "leave_date" in update_dict:
        update_dict["date"] = update_dict.pop("leave_date")  # map to model's "date" column

    for key, value in update_dict.items():
        setattr(leave, key, value)

    db.commit()
    db.refresh(leave)
    return leave


# ---------------- Delete Leave by ID ----------------
@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave/Holiday not found")

    db.delete(leave)
    db.commit()
    return {"message": "Leave/Holiday deleted successfully"}
>>>>>>> origin/main
