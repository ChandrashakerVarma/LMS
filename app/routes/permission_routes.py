from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.permission_m import Permission
from app.models.user_m import User
from app.models.shift_m import Shift
from app.Schema.permission_schema import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse
)
from app.dependencies import get_current_user

# 🔐 Permission checks
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

MENU_ID = 46

router = APIRouter(prefix="/permissions", tags=["Permissions"])


# ➕ CREATE PERMISSION
@router.post(
    "/", 
    response_model=PermissionResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(menu_id=MENU_ID))]
)
def create_permission(
    data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = db.query(Shift).filter(Shift.id == data.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

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

    new_permission = Permission(
        **data.dict(),
        created_by=current_user.first_name
    )

    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)

    return new_permission


# 📋 GET ALL PERMISSIONS
@router.get(
    "/", 
    response_model=List[PermissionResponse],
    dependencies=[Depends(require_view_permission(menu_id=MENU_ID))]
)
def get_all_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Permission).all()


# 🔍 GET PERMISSION BY ID
@router.get(
    "/{permission_id}", 
    response_model=PermissionResponse,
    dependencies=[Depends(require_view_permission(menu_id=MENU_ID))]
)
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
@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    dependencies=[Depends(require_edit_permission(menu_id=MENU_ID))]
)
def update_permission(
    permission_id: int,
    updated_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(permission, key, value)

    permission.modified_by = current_user.first_name
    permission.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(permission)

    return permission


# ❌ DELETE PERMISSION
@router.delete(
    "/{permission_id}",
    dependencies=[Depends(require_delete_permission(menu_id=MENU_ID))]
)
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
