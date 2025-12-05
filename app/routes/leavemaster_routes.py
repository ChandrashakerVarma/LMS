# app/routes/leave_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.leavemaster_m import LeaveMaster
from app.models.user_m import User
from app.schema.leavemaster_schema import (
    LeaveMasterCreate,
    LeaveMasterUpdate,
    LeaveMasterResponse
)
from app.dependencies import get_current_user

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

MENU_ID = 45

router = APIRouter(prefix="/leaves", tags=["Leaves"])


# ---------------- CREATE ----------------
@router.post(
    "/", 
    response_model=LeaveMasterResponse,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_leave(
    data: LeaveMasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_leave = LeaveMaster(
        **data.dict(),
        created_by=current_user.first_name
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return new_leave


# ---------------- GET ALL ----------------
@router.get(
    "/", 
    response_model=List[LeaveMasterResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(LeaveMaster).all()


# ---------------- GET BY ID ----------------
@router.get(
    "/{leave_id}",
    response_model=LeaveMasterResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    return leave


# ---------------- UPDATE ----------------
@router.put(
    "/{leave_id}",
    response_model=LeaveMasterResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_leave(
    leave_id: int,
    data: LeaveMasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()

    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    update_data = data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(leave, key, value)

    leave.modified_by = current_user.first_name
    leave.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(leave)

    return leave


# ---------------- DELETE ----------------
@router.delete(
    "/{leave_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = db.query(LeaveMaster).filter(LeaveMaster.id == leave_id).first()

    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    db.delete(leave)
    db.commit()

    return {"message": f"Leave deleted by {current_user.first_name}"}
