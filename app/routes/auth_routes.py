from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_m import User
from app.models.role_m import Role
from app.schema.user_schema import AuthRegister, AuthRegisterResponse
from app.utils.utils import hash_password, verify_password, create_access_token,decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------- REGISTER ----------------
@router.post("/register", response_model=AuthRegisterResponse)
def register_user(payload: AuthRegister, db: Session = Depends(get_db)):
    # Check if email already exists
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role_id
    if payload.role_id:
        role = db.query(Role).filter(Role.id == payload.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id")

    # Create user
    new_user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=payload.role_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return minimal response
    return AuthRegisterResponse(
        name=new_user.name,
        email=new_user.email,
        role_id=new_user.role_id,
        password=payload.password
    )


# ---------------- LOGIN ----------------
@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}