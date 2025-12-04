from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.role_m import Role
from app.schemas.role_schema import RoleCreate, RoleUpdate, RoleResponse
from app.dependencies import get_current_user
from app.models.user_m import User

# Permission-based access control
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/roles", tags=["Roles"])

MENU_ID = 4   # Roles Menu ID


# -----------------------------------------------------------
# CREATE ROLE
# -----------------------------------------------------------
@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_role = db.query(Role).filter(Role.name == data.name).first()
    if existing_role:
        raise HTTPException(400, "Role with this name already exists")

    new_role = Role(name=data.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


# -----------------------------------------------------------
# GET ALL ROLES
# -----------------------------------------------------------
@router.get(
    "/",
    response_model=List[RoleResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Role).order_by(Role.id.asc()).all()


# -----------------------------------------------------------
# GET SINGLE ROLE BY ID
# -----------------------------------------------------------
@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_role_by_id(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")

    return role


# -----------------------------------------------------------
# UPDATE ROLE
# -----------------------------------------------------------
@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")

    # Check duplicate name
    if data.name:
        exists = (
            db.query(Role)
            .filter(Role.name == data.name, Role.id != role_id)
            .first()
        )
        if exists:
            raise HTTPException(400, "Role name already exists")

        role.name = data.name

    db.commit()
    db.refresh(role)
    return role


# -----------------------------------------------------------
# DELETE ROLE
# -----------------------------------------------------------
@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")

    db.delete(role)
    db.commit()
    return None
