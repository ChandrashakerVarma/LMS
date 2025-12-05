from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_m import User
from app.utils.utils import decode_access_token

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================
# Get current authenticated user
# ============================================
def get_current_user(
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db)
) -> User:

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # User inactive?
    if user.inactive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated"
        )

    # Organization-level checks
    if user.organization_id:
        org = user.organization
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        if not org.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organization has been suspended."
            )

        # Subscription checks
        if org.subscription_status not in ["active", "trial"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Organization subscription is {org.subscription_status}"
            )

        from datetime import date
        if org.subscription_end_date and org.subscription_end_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Organization subscription expired"
            )

    return user


# ============================================
# ROLE-BASED ACCESS CONTROL (UPDATED)
# ============================================

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow only super_admin"""
    if not current_user.role or current_user.role.name != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    return current_user


def require_org_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow org_admin or super_admin"""
    if current_user.role and current_user.role.name in ["super_admin", "org_admin"]:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Organization Admin access required"
    )


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """Allow manager"""
    if not current_user.role or current_user.role.name != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user


def require_employee(current_user: User = Depends(get_current_user)) -> User:
    """Allow employee"""
    if not current_user.role or current_user.role.name != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )
    return current_user


def require_manager_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow manager, org_admin, super_admin"""
    if current_user.role and current_user.role.name in ["manager", "org_admin", "super_admin"]:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Manager or Admin access required"
    )


def require_any_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow org_admin or super_admin"""
    if current_user.role and current_user.role.name in ["org_admin", "super_admin"]:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    )


# ============================================
# ORGANIZATION VALIDATION
# ============================================

def require_organization(current_user: User = Depends(get_current_user)) -> User:
    """User must belong to org (Super admin exempt)"""
    if current_user.role and current_user.role.name == "super_admin":
        return current_user

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must belong to an organization"
        )
    return current_user


def require_same_organization(user_id: int):
    """Ensure target user belongs to same org (super_admin exempt)"""

    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.role and current_user.role.name == "super_admin":
            return current_user

        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: different organization"
            )
        return current_user

    return dependency


# ============================================
# OPTIONAL USER (no error if unauthorized)
# ============================================

def get_current_user_optional(
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db)
):
    try:
        return get_current_user(token, db)
    except:
        return None


# ============================================
# ORG ACCESS CHECK
# ============================================

def has_organization_access(current_user: User, target_org_id: int):
    if current_user.role and current_user.role.name == "super_admin":
        return True
    return current_user.organization_id == target_org_id


def validate_organization_access(
    target_organization_id: int,
    current_user: User = Depends(get_current_user)
):
    if not has_organization_access(current_user, target_organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    return current_user
