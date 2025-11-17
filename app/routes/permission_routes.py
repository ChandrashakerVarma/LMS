# app/routes/permission_r.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.permission_m import Permission
from app.models.shift_m import Shift
from app.models.user_m import User
from app.schema.permission_schema import PermissionCreate, PermissionUpdate, PermissionResponse
from app.dependencies import require_admin, require_user

router = APIRouter(prefix="/permissions", tags=["Permissions"])


# 🟢 CREATE Permission (Manager allocates permission)
@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Manager/Admin access only
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = db.query(Shift).filter(Shift.id == data.shift_id, Shift.status == "active").first()
    if not shift:
        raise HTTPException(status_code=400, detail="Selected shift is not available or inactive")

    # Check if user already has a permission for the same date and shift
    existing = (
        db.query(Permission)
        .filter(Permission.user_id == data.user_id, Permission.date == data.date, Permission.shift_id == data.shift_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists for this shift and date")

    permission = Permission(
        user_id=data.user_id,
        shift_id=data.shift_id,
        date=data.date,
        reason=data.reason,
        status="pending"
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


# 🟡 GET all Permissions (Admin/Manager only)
@router.get("/", response_model=List[PermissionResponse])
def get_all_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return db.query(Permission).all()


# 🟠 GET Permission by User (User or Manager)
@router.get("/user/{user_id}", response_model=List[PermissionResponse])
def get_permissions_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(Permission).filter(Permission.user_id == user_id).all()


# 🔵 UPDATE Permission Status (Manager updates: approve / cancel)
@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission_status(
    permission_id: int,
    data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Manager/Admin
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if data.status not in ["approved", "cancelled", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status update")

    # Update allowed fields
    if data.reason is not None:
        permission.reason = data.reason
    permission.status = data.status

    db.commit()
    db.refresh(permission)
    return permission


# 🔴 DELETE Permission (Admin/Manager)
@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(permission)
    db.commit()
    return None
