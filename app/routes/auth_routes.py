from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_m import User
from app.models.role_m import Role
from app.schema.user_schema import AuthRegister, AuthRegisterResponse, UserCreate
from app.utils.utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------- REGISTER ----------------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Ensure default role exists
    default_role = db.query(Role).filter(Role.name == "user").first()
    if not default_role:
        default_role = Role(name="user")
        db.add(default_role)
        db.commit()
        db.refresh(default_role)

    # Hash user password
    hashed_password = hash_password(user.password)

    # Create user properly
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,   # FIXED
        role_id=default_role.id            # FIXED
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}



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

