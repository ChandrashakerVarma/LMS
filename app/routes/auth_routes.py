from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema import user_schema
from app.models.user_m import User
from app.models.role_m import Role
from app.utils import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=user_schema.UserResponse)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if role exists
    db_role = None
    if user.role_id:
        db_role = db.query(Role).filter(Role.id == user.role_id).first()
        if not db_role:
            raise HTTPException(status_code=400, detail="Invalid role_id")

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role_id=user.role_id,
        date_of_birth=user.date_of_birth,
        joining_date=user.joining_date,
        relieving_date=user.relieving_date,
        address=user.address,
        # photo=user.photo,
        designation=user.designation
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=user_schema.UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=user_schema.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[user_schema.UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
