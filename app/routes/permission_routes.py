from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.permission_m import Permission
from app.models.user_m import User
from app.models.shift_m import Shift
from app.schema.permission_schema import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse
)
from app.dependencies import get_current_user   

router = APIRouter(prefix="/permissions", tags=["Permissions"])


# ➕ CREATE PERMISSION
@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)   # 🔐 track who created
):
    # Validate user exists
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate shift exists
    shift = db.query(Shift).filter(Shift.id == data.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    # Check duplicate permission (same user + same date)
    exists = (
        db.query(Permission)
        .filter(Permission.user_id == data.user_id,
                Permission.date == data.date)
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=400,
            detail="Permission request for this user on this date already exists"
        )

    # Create permission
    new_permission = Permission(
        **data.dict(),
        created_by=current_user.first_name  # 👈 only set on creation
    )

    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)

    return new_permission


# 📋 GET ALL PERMISSIONS
@router.get("/", response_model=List[PermissionResponse])
def get_all_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Permission).all()


# 🔍 GET PERMISSION BY ID
@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission_by_id(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    return permission


# ✏️ UPDATE PERMISSION
@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    updated_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    # Update only provided fields
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(permission, key, value)

    # Audit fields
    permission.modified_by = current_user.first_name
    permission.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(permission)

    return permission


# ❌ DELETE PERMISSION
@router.delete("/{permission_id}")
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(permission)
    db.commit()

    return {"message": "Permission deleted successfully"}
