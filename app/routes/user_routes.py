from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user_m import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/users", tags=["Users"])

MENU_ID = 3  # Example: change based on your menu structure


# Create User
@router.post("/", response_model=UserResponse,
             dependencies=[Depends(require_create_permission(MENU_ID))])
def create_user(payload: UserCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        role_id=payload.role_id,
        organization_id=current_user.organization_id,
        created_by=current_user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# List Users
@router.get("/", response_model=List[UserResponse],
            dependencies=[Depends(require_view_permission(MENU_ID))])
def list_users(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):

    return db.query(User).filter(
        User.organization_id == current_user.organization_id
    ).all()


# Get user by ID
@router.get("/{user_id}", response_model=UserResponse,
            dependencies=[Depends(require_view_permission(MENU_ID))])
def get_user_by_id(user_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Update User
@router.put("/{user_id}", response_model=UserResponse,
            dependencies=[Depends(require_edit_permission(MENU_ID))])
def update_user(user_id: int,
                payload: UserUpdate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# Delete User
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_delete_permission(MENU_ID))])
def delete_user(user_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None
