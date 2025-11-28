from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.role_right_m import RoleRight
from app.models.role_m import Role
from app.models.menu_m import Menu
from app.Schema.role_right_schema import (
    RoleRightCreate, 
    RoleRightUpdate, 
    RoleRightResponse,
    RoleRightWithMenuResponse,
    BulkRoleRightRequest
)
from app.dependencies import require_admin, get_current_user
from app.models.user_m import User

router = APIRouter(prefix="/role-rights", tags=["Role Rights"])

# ---------------- CREATE ROLE RIGHT ----------------
@router.post("/", response_model=RoleRightResponse, status_code=status.HTTP_201_CREATED)
def create_role_right(
    payload: RoleRightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Check if role exists
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if menu exists
    menu = db.query(Menu).filter(Menu.id == payload.menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Check if role right already exists
    existing = db.query(RoleRight).filter(
        RoleRight.role_id == payload.role_id,
        RoleRight.menu_id == payload.menu_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Role right already exists for this role and menu combination"
        )
    
    new_role_right = RoleRight(
        role_id=payload.role_id,
        menu_id=payload.menu_id,
        can_view=payload.can_view,
        can_create=payload.can_create,
        can_edit=payload.can_edit,
        can_delete=payload.can_delete,
        created_by=current_user.email,
        modified_by=current_user.email
    )
    
    db.add(new_role_right)
    db.commit()
    db.refresh(new_role_right)
    return new_role_right

# ---------------- BULK CREATE/UPDATE ROLE RIGHTS ----------------
@router.post("/bulk", response_model=dict)
def bulk_upsert_role_rights(
    payload: BulkRoleRightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Check if role exists
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    created = 0
    updated = 0
    
    for right in payload.rights:
        # Check if menu exists
        menu = db.query(Menu).filter(Menu.id == right.menu_id).first()
        if not menu:
            continue
        
        # Check if exists
        existing = db.query(RoleRight).filter(
            RoleRight.role_id == payload.role_id,
            RoleRight.menu_id == right.menu_id
        ).first()
        
        if existing:
            # Update
            existing.can_view = right.can_view
            existing.can_create = right.can_create
            existing.can_edit = right.can_edit
            existing.can_delete = right.can_delete
            existing.modified_by = current_user.email
            updated += 1
        else:
            # Create
            new_right = RoleRight(
                role_id=payload.role_id,
                menu_id=right.menu_id,
                can_view=right.can_view,
                can_create=right.can_create,
                can_edit=right.can_edit,
                can_delete=right.can_delete,
                created_by=current_user.email,
                modified_by=current_user.email
            )
            db.add(new_right)
            created += 1
    
    db.commit()
    return {
        "message": "Bulk operation completed",
        "created": created,
        "updated": updated
    }

# ---------------- GET ALL ROLE RIGHTS ----------------
@router.get("/", response_model=List[RoleRightResponse])
def get_all_role_rights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    role_rights = db.query(RoleRight).all()
    return role_rights

# ---------------- GET ROLE RIGHTS BY ROLE ----------------
@router.get("/role/{role_id}", response_model=List[RoleRightWithMenuResponse])
def get_role_rights_by_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if role exists
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role_rights = (
        db.query(RoleRight)
        .options(joinedload(RoleRight.menu))
        .filter(RoleRight.role_id == role_id)
        .all()
    )
    
    result = []
    for rr in role_rights:
        result.append(
            RoleRightWithMenuResponse(
                id=rr.id,
                menu_id=rr.menu_id,
                menu_name=rr.menu.name if rr.menu else "",
                menu_display_name=rr.menu.display_name if rr.menu else "",
                menu_route=rr.menu.route if rr.menu else None,
                can_view=rr.can_view,
                can_create=rr.can_create,
                can_edit=rr.can_edit,
                can_delete=rr.can_delete
            )
        )
    
    return result

# ---------------- GET ROLE RIGHT BY ID ----------------
@router.get("/{role_right_id}", response_model=RoleRightResponse)
def get_role_right_by_id(
    role_right_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role_right = db.query(RoleRight).filter(RoleRight.id == role_right_id).first()
    if not role_right:
        raise HTTPException(status_code=404, detail="Role right not found")
    return role_right

# ---------------- UPDATE ROLE RIGHT ----------------
@router.put("/{role_right_id}", response_model=RoleRightResponse)
def update_role_right(
    role_right_id: int,
    payload: RoleRightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    role_right = db.query(RoleRight).filter(RoleRight.id == role_right_id).first()
    if not role_right:
        raise HTTPException(status_code=404, detail="Role right not found")
    
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(role_right, key, value)
    
    role_right.modified_by = current_user.email
    
    db.commit()
    db.refresh(role_right)
    return role_right

# ---------------- DELETE ROLE RIGHT ----------------
@router.delete("/{role_right_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role_right(
    role_right_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    role_right = db.query(RoleRight).filter(RoleRight.id == role_right_id).first()
    if not role_right:
        raise HTTPException(status_code=404, detail="Role right not found")
    
    db.delete(role_right)
    db.commit()
    return None

# ---------------- CHECK USER PERMISSION ----------------
@router.get("/check-permission/{menu_id}")
def check_user_permission(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if current user has permission for a specific menu"""
    role_right = (
        db.query(RoleRight)
        .filter(
            RoleRight.role_id == current_user.role_id,
            RoleRight.menu_id == menu_id
        )
        .first()
    )
    
    if not role_right:
        return {
            "can_view": False,
            "can_create": False,
            "can_edit": False,
            "can_delete": False
        }
    
    return {
        "can_view": role_right.can_view,
        "can_create": role_right.can_create,
        "can_edit": role_right.can_edit,
        "can_delete": role_right.can_delete
    }
