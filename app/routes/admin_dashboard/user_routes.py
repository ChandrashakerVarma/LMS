from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from passlib.context import CryptContext

from app.database import get_db
from app.models.user_m import User
from app.models.role_m import Role
from app.models.branch_m import Branch
from app.models.organization import Organization
from app.schema.user_schema import UserCreate, UserUpdate, UserResponse
from app.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- CREATE ----------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(payload.password)
    new_user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_password,
        role_id=payload.role_id,
        branch_id=payload.branch_id,
        organization_id=payload.organization_id,
        address=payload.address,
        designation=payload.designation,
        date_of_birth=payload.date_of_birth,
        joining_date=payload.joining_date,
        relieving_date=payload.relieving_date
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return map_user_response(new_user)


# ---------------- READ ALL ----------------
@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    users = db.query(User).options(
        joinedload(User.role),
        joinedload(User.branch),
        joinedload(User.organization)
    ).all()
    return [map_user_response(u) for u in users]


# ---------------- READ BY ID ----------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(User).options(
        joinedload(User.role),
        joinedload(User.branch),
        joinedload(User.organization)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Non-admins can only see their own profile
    if current_user["role"] != "admin" and current_user["id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return map_user_response(user)


# ---------------- UPDATE ----------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.password:
        payload.password = pwd_context.hash(payload.password)

    for key, value in payload.dict(exclude_unset=True).items():
        if key == "password":
            setattr(user, "hashed_password", value)
        else:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return map_user_response(user)


# ---------------- DELETE ----------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# ---------------- HELPER ----------------
def map_user_response(user: User) -> UserResponse:
    """Map ORM object to schema-friendly format"""
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        branch_id=user.branch_id,
        organization_id=user.organization_id,
        address=user.address,
        designation=user.designation,
        inactive=user.inactive,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
        date_of_birth=user.date_of_birth,
        joining_date=user.joining_date,
        relieving_date=user.relieving_date
    )
