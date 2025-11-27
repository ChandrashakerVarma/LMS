from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.schema.user_schema import UserCreate, UserResponse,UserBase,UserUpdate
from app.models.user_m import User
from app.utils.utils import hash_password
from app.dependencies import require_admin

router = APIRouter(prefix="/users", tags=["Users"])

# ---------- CREATE User ----------

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Check duplicate email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        **payload.dict(exclude={"password"}),  # All fields except password
        hashed_password=hash_password(payload.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # This is the fix for Pydantic v2 + SQLAlchemy relationships
    return UserResponse.model_validate(new_user)
# ---------- READ - Get All Users ----------
@router.get("/", response_model=list[UserResponse])
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
@router.get("/{user_id}", response_model=UserResponse)
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

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return UserResponse.from_orm(db_user)   # ✅ FIX


# =====================================================
# delete user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
