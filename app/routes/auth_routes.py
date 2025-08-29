from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.Schema import user_schema
from app.models.user_m import User
from app.models.role_m import Role  # make sure Role model is imported
from app.utils import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


from app.models.role_m import Role  # make sure Role model is imported

@router.post("/register", response_model=user_schema.UserResponse)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    # check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # check if role exists
    db_role = db.query(Role).filter(Role.id == user.role_id).first()
    if not db_role:
        raise HTTPException(status_code=400, detail="Invalid role_id")

    # create new user
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role_id=user.role_id,
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

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}
