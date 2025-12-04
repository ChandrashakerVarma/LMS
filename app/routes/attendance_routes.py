from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.attendance_m import Attendance
from app.schemas.attendance_schema import AttendanceResponse
from app.dependencies import get_current_user

# Permissions
from app.permission_dependencies import (
    require_view_permission,
    require_delete_permission,
)

ATTENDANCE_MENU_ID = 44

router = APIRouter(prefix="/attendance", tags=["Attendance Records"])


# ------------------------------------------------
# GET ALL ATTENDANCE RECORDS
# ------------------------------------------------
@router.get(
    "/",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_all_attendance(db: Session = Depends(get_db)):
    return db.query(Attendance).order_by(Attendance.id.desc()).all()


# ------------------------------------------------
# GET ATTENDANCE BY ID
# ------------------------------------------------
@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not record:
        raise HTTPException(404, "Attendance record not found")

    return record


# ------------------------------------------------
# DELETE ATTENDANCE ENTRY
# ------------------------------------------------
@router.delete(
    "/{attendance_id}",
    dependencies=[Depends(require_delete_permission(ATTENDANCE_MENU_ID))]
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not record:
        raise HTTPException(404, "Attendance record not found")

    db.delete(record)
    db.commit()

    return {"message": f"Attendance deleted by {current_user.first_name}"}
