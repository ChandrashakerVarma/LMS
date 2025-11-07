from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.role_m import Role
from app.schema.role_schema import RoleCreate, RoleUpdate, RoleResponse
from app.dependencies import require_admin  # ✅ Only Admins can manage roles

router = APIRouter(prefix="/roles", tags=["Roles"])


# 🟢 Create Role (Admin Only)
@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Create a new role — Admin access only.
    """
    existing_role = db.query(Role).filter(Role.name == data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=400, detail="Role with this name already exists"
        )

    new_role = Role(name=data.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


# 🟡 Get All Roles (Admin Only)
@router.get("/", response_model=List[RoleResponse])
def get_all_roles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retrieve all roles — ordered by ID (ascending).
    """
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return roles


# 🟠 Get Role by ID (Admin Only)
@router.get("/{role_id}", response_model=RoleResponse)
def get_role_by_id(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retrieve a single role by ID — Admin access only.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


# 🔵 Update Role (Admin Only)
@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Update role name — Admin access only.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if data.name:
        existing = (
            db.query(Role)
            .filter(Role.name == data.name, Role.id != role_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Role name already exists")

        role.name = data.name

    db.commit()
    db.refresh(role)
    return role


# 🔴 Delete Role (Admin Only)
@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Delete a role by ID — Admin access only.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()
    return None
