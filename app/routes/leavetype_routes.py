from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import List

from app.database import get_db
from app.models.leavetype_m import LeaveType
from app.models.user_m import User
from app.schema.leavetype_schema import (
    LeaveTypeCreate,
    LeaveTypeUpdate,
    LeaveTypeResponse
)
from app.dependencies import get_current_user

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

# Assign the correct MENU_ID for Leave Type module
MENU_ID = 45

router = APIRouter(prefix="/leave-types", tags=["Leave Types"])


# ============================================================
# CREATE Leave Type
# ============================================================
@router.post(
    "/",
    response_model=LeaveTypeResponse,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_leave_type(
    payload: LeaveTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave_type = LeaveType(
        **payload.model_dump(),
        created_by=current_user.first_name
    )

    db.add(leave_type)
    db.commit()
    db.refresh(leave_type)

    return leave_type


# ============================================================
# GET ALL Leave Types
# ============================================================
@router.get(
    "/",
    response_model=List[LeaveTypeResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_leave_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(LeaveType).all()


# ============================================================
# GET Leave Type BY ID
# ============================================================
@router.get(
    "/{leave_type_id}",
    response_model=LeaveTypeResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_leave_type(
    leave_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave_type = db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()

    if not leave_type:
        raise HTTPException(status_code=404, detail="Leave Type not found")

    return leave_type


# ============================================================
# UPDATE Leave Type
# ============================================================
@router.put(
    "/{leave_type_id}",
    response_model=LeaveTypeResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_leave_type(
    leave_type_id: int,
    payload: LeaveTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave_type = db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()

    if not leave_type:
        raise HTTPException(status_code=404, detail="Leave Type not found")

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(leave_type, field, value)

    leave_type.modified_by = current_user.first_name
    leave_type.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(leave_type)

    return leave_type


# ============================================================
# DELETE Leave Type
# ============================================================
@router.delete(
    "/{leave_type_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_leave_type(
    leave_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave_type = db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()

    if not leave_type:
        raise HTTPException(status_code=404, detail="Leave Type not found")

    db.delete(leave_type)
    db.commit()

    return {"message": f"Leave Type deleted by {current_user.first_name}"}
