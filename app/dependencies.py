from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user_m import User
from app.utils.utils import decode_access_token

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # ✅ Eager load role to avoid None in require_admin()
    user = (
        db.query(User)
        .options(joinedload(User.role))  # this line ensures role data is available
        .filter(User.id == payload.get("sub"))
        .first()
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.role or user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


def require_user(user: User = Depends(get_current_user)) -> User:
    if not user.role or user.role.name.lower() != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return user
