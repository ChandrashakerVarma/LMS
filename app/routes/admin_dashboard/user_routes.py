from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.schema import user_schema
from app.models.user_m import User
from app.utils import hash_password
from app.dependencies import require_admin

router = APIRouter(prefix="/users", tags=["Users"])

# ---------- CREATE User ----------
@router.post("/", response_model=user_schema.UserResponse)
def create_user(
    user: user_schema.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Check if email exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role_id=user.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Eager load role and progress for response
    db.refresh(new_user)
    return db.query(User).options(
        selectinload(User.role),
        selectinload(User.progress)
    ).filter(User.id == new_user.id).first()


# ---------- READ - Get All Users ----------
@router.get("/", response_model=list[user_schema.UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = db.query(User).options(
        selectinload(User.role),
        selectinload(User.progress)
    ).all()
    return users


# ---------- READ - Get Single User ----------
@router.get("/{user_id}", response_model=user_schema.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # User can see own profile, admin can see all
):
    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.progress)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Allow only self or admin to view
    if current_user.id != user_id and current_user.role_id != 1:  # Assuming role_id=1 is admin
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return user


# ---------- UPDATE User ----------
@router.put("/{user_id}", response_model=user_schema.UserResponse)
def update_user(
    user_id: int,
    updated_user: user_schema.UserBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.name = updated_user.name
    user.email = updated_user.email
    user.role_id = updated_user.role_id

    db.commit()
    db.refresh(user)

    # Eager load role and progress for response
    return db.query(User).options(
        selectinload(User.role),
        selectinload(User.progress)
    ).filter(User.id == user.id).first()


# ---------- DELETE User ----------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return None
