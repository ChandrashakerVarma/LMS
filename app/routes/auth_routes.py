from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_m import User
from app.models.role_m import Role
from app.Schema.user_schema import AuthRegister, AuthRegisterResponse
from app.utils.utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------- REGISTER ----------------
@router.post("/register", response_model=AuthRegisterResponse)
def register(user: AuthRegister, db: Session = Depends(get_db)):
    """✅ Open registration — anyone can create an account"""
    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role_id (optional)
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id")

    # ✅ Create new user (no 'name' field — use first_name / last_name)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role_id=user.role_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return AuthRegisterResponse(
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        email=new_user.email,
        role_id=new_user.role_id
    )


# ---------------- LOGIN ----------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """✅ User login with email and password"""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Fetch role details (if any)
    role_name = user.role.name if user.role else None
    role_id = user.role.id if user.role else None

    # ✅ Return token + user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name or ''}".strip(),
            "email": user.email,
            "role_id": role_id,
            "role_name": role_name
        }
    }
