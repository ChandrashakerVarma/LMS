from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_m import User
from app.models.role_right_m import RoleRight
from app.dependencies import get_current_user

def check_menu_permission(menu_id: int, permission_type: str = "view"):
    """
    Dependency to check if user has specific permission for a menu
    
    Args:
        menu_id: ID of the menu to check permission for
        permission_type: Type of permission - "view", "create", "edit", "delete"
    
    Returns:
        Function that checks permission and returns user if authorized
    """
    def permission_checker(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> User:
        # Admin always has access
        if current_user.role and current_user.role.name.lower() == "admin":
            return current_user
        
        # Check role rights
        role_right = db.query(RoleRight).filter(
            RoleRight.role_id == current_user.role_id,
            RoleRight.menu_id == menu_id
        ).first()
        
        if not role_right:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No access to this resource"
            )
        
        # Check specific permission
        permission_map = {
            "view": role_right.can_view,
            "create": role_right.can_create,
            "edit": role_right.can_edit,
            "delete": role_right.can_delete
        }
        
        if not permission_map.get(permission_type, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have {permission_type} permission for this resource"
            )
        
        return current_user
    
    return permission_checker


# Specific permission checkers for common use cases
def require_view_permission(menu_id: int):
    """Require view permission for a menu"""
    return check_menu_permission(menu_id, "view")

def require_create_permission(menu_id: int):
    """Require create permission for a menu"""
    return check_menu_permission(menu_id, "create")

def require_edit_permission(menu_id: int):
    """Require edit permission for a menu"""
    return check_menu_permission(menu_id, "edit")

def require_delete_permission(menu_id: int):
    """Require delete permission for a menu"""
    return check_menu_permission(menu_id, "delete")


# Helper function to check permission programmatically (not as dependency)
def has_permission(
    user: User,
    menu_id: int,
    permission_type: str,
    db: Session
) -> bool:
    """
    Check if a user has a specific permission for a menu
    
    Args:
        user: User object
        menu_id: Menu ID to check
        permission_type: "view", "create", "edit", or "delete"
        db: Database session
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    # Admin always has access
    if user.role and user.role.name.lower() == "admin":
        return True
    
    role_right = db.query(RoleRight).filter(
        RoleRight.role_id == user.role_id,
        RoleRight.menu_id == menu_id
    ).first()
    
    if not role_right:
        return False
    
    permission_map = {
        "view": role_right.can_view,
        "create": role_right.can_create,
        "edit": role_right.can_edit,
        "delete": role_right.can_delete
    }
    
    return permission_map.get(permission_type, False)
