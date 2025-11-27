from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_m import User
from app.utils.utils import decode_access_token

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Get current authenticated user
def get_current_user(
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db)
) -> User:

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ---- ROLE CHECKS ---- #

def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access required"
        )
    return current_user



def require_user(user: User = Depends(get_current_user)) -> User:
    if not user.role or user.role.name.lower() != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return user


def require_manager(user: User = Depends(get_current_user)) -> User:
    if not user.role or user.role.name.lower() != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return user


def require_manager_or_admin(user: User = Depends(get_current_user)):
    if user.role.name.lower() not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Admin or Manager access required"
        )
    return user
