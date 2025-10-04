from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.schema.user_schema import UserCreate, UserResponse
from app.models.user_m import User
from app.models.role_m import Role
from app.utils import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# Register
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role_id
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id")

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role_id=user.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return as Pydantic model
    return UserResponse.from_orm(new_user)


# Login
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# Get logged-in user
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)


# Get specific user
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


# List all users
@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserResponse.from_orm(u) for u in users]
