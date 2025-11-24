from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from passlib.context import CryptContext

from app.database import get_db
from app.models.user_m import User
from app.schema.user_schema import UserCreate, UserUpdate, UserResponse
from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_MENU_ID = 2    # ⭐ Update if needed


# ---------------- CREATE ----------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_create_permission(USERS_MENU_ID))  # ⭐ CREATE permission
):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(payload.password)

    new_user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        hashed_password=hashed_password,
        role_id=payload.role_id,
        branch_id=payload.branch_id,
        organization_id=payload.organization_id,
        date_of_birth=payload.date_of_birth,
        joining_date=payload.joining_date,
        relieving_date=payload.relieving_date,
        address=payload.address,
        designation=payload.designation,
        inactive=payload.inactive,
        biometric_id=payload.biometric_id,

        created_by=current_user.email,
        modified_by=current_user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return map_user_response(new_user)


# ---------------- READ ALL ----------------
@router.get("/", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_view_permission(USERS_MENU_ID))  # ⭐ VIEW permission
):
    users = db.query(User).options(
        joinedload(User.role),
        joinedload(User.branch),
        joinedload(User.organization),
    ).all()
    return [map_user_response(u) for u in users]


# ---------------- READ BY ID ----------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(USERS_MENU_ID))  # ⭐ VIEW permission
):
    user = db.query(User).options(
        joinedload(User.role),
        joinedload(User.branch),
        joinedload(User.organization),
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Extra rule: Non-admins can only view themselves
    role_name = (getattr(current_user.role, "name", "") or "").lower()
    if role_name != "admin" and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return map_user_response(user)


# ---------------- UPDATE ----------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_edit_permission(USERS_MENU_ID))  # ⭐ EDIT permission
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    user.modified_by = current_user.email

    db.commit()
    db.refresh(user)
    return map_user_response(user)


# ---------------- DELETE ----------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_delete_permission(USERS_MENU_ID))  # ⭐ DELETE permission
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# ---------------- HELPER ----------------
def map_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role_id=user.role_id,
        branch_id=user.branch_id,
        organization_id=user.organization_id,
        date_of_birth=user.date_of_birth,
        joining_date=user.joining_date,
        relieving_date=user.relieving_date,
        address=user.address,
        designation=user.designation,
        inactive=user.inactive,
        biometric_id=user.biometric_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        created_by=user.created_by,
        modified_by=user.modified_by,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
    )
