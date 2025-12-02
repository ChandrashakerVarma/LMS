# ENHANCED app/routes/admin_dashboard/user_routes.py
# ✅ Adds OPTIONAL fuzzy search to GET /users/ endpoint
# ✅ All existing functionality UNCHANGED
# ✅ Backward compatible

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.schema.user_schema import (
    UserCreate, 
    UserResponse, 
    UserDetailResponse,
    UserUpdate
)
from app.models.user_m import User
from app.models.role_m import Role
from app.models.branch_m import Branch
from app.models.organization_m import Organization
from app.utils.utils import hash_password
from app.dependencies import get_current_user
from app.middleware.tenant_limits import TenantLimitsMiddleware
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/users", tags=["Users"])
USERS_MENU_ID = 3


# ============================================
# HELPER: Validate Role Assignment (UNCHANGED)
# ============================================
def validate_role_assignment(current_user: User, target_role: Role) -> bool:
    """✅ UNCHANGED"""
    current_role_name = current_user.role.name.lower() if current_user.role else None
    target_role_name = target_role.name.lower()
    
    if current_role_name == "super_admin":
        return True
    
    if current_user.is_org_admin or current_role_name == "org_admin":
        allowed_roles = ["org_admin", "manager", "employee"]
        if target_role_name not in allowed_roles:
            return False
        return True
    
    if current_role_name == "manager":
        return target_role_name == "employee"
    
    return False


# ============================================
# CREATE USER (UNCHANGED)
# ============================================
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(USERS_MENU_ID))
):
    """✅ UNCHANGED - Original create_user logic"""
    
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must belong to an organization to create users"
        )
    
    await TenantLimitsMiddleware.check_user_limit(
        organization_id=current_user.organization_id,
        db=db
    )
    
    existing_user = db.query(User).filter(
        and_(
            User.email == payload.email.lower(),
            User.organization_id == current_user.organization_id
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in your organization"
        )
    
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id"
        )
    
    if not validate_role_assignment(current_user, role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to assign '{role.name}' role. "
                   f"Contact your administrator for assistance."
        )
    
    if payload.branch_id:
        branch = db.query(Branch).filter(
            and_(
                Branch.id == payload.branch_id,
                Branch.organization_id == current_user.organization_id
            )
        ).first()
        
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Branch not found or doesn't belong to your organization"
            )
    
    user_data = payload.dict(exclude={"password"})
    user_data["organization_id"] = current_user.organization_id
    user_data["hashed_password"] = hash_password(payload.password)
    
    user_data["is_org_admin"] = (
        role.name.lower() == "org_admin" and 
        (current_user.is_org_admin or current_user.role.name.lower() == "super_admin")
    )
    
    user_data["created_by"] = f"{current_user.first_name} {current_user.last_name}"
    
    new_user = User(**user_data)
    
    db.add(new_user)
    db.commit()
    
    TenantLimitsMiddleware.update_user_count(
        organization_id=current_user.organization_id,
        db=db,
        increment=True
    )
    
    db.refresh(new_user)
    return UserResponse.model_validate(new_user)


# ============================================
# GET AVAILABLE ROLES (UNCHANGED)
# ============================================
@router.get("/available-roles")
async def get_available_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ UNCHANGED"""
    current_role_name = current_user.role.name.lower() if current_user.role else None
    
    if current_role_name == "super_admin":
        allowed_role_names = ["super_admin", "org_admin", "manager", "employee"]
    elif current_user.is_org_admin or current_role_name == "org_admin":
        allowed_role_names = ["org_admin", "manager", "employee"]
    elif current_role_name == "manager":
        allowed_role_names = ["employee"]
    else:
        allowed_role_names = []
    
    if not allowed_role_names:
        return []
    
    roles = db.query(Role).filter(
        Role.name.in_(allowed_role_names)
    ).all()
    
    return [
        {
            "id": role.id,
            "name": role.name,
            "display_name": role.name.replace("_", " ").title()
        }
        for role in roles
    ]


# ============================================
# ✅ ENHANCED: GET ALL USERS with OPTIONAL Fuzzy Search
# ============================================
@router.get("/", response_model=List[UserDetailResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    inactive: Optional[bool] = None,
    search: Optional[str] = None,  # EXISTING search parameter
    
    # ✅ NEW: Optional fuzzy search parameters
    use_fuzzy_search: bool = Query(
        False, 
        description="Enable ML-powered fuzzy search (typo-tolerant)"
    ),
    fuzzy_query: Optional[str] = Query(
        None, 
        description="Fuzzy search query (overrides 'search' if provided)"
    ),
    fuzzy_threshold: int = Query(
        70,
        ge=50,
        le=100,
        description="Fuzzy match threshold (50-100, higher=more strict)"
    ),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(USERS_MENU_ID))
):
    """
    ✅ ENHANCED: Get all users with OPTIONAL fuzzy search
    
    **Default behavior (use_fuzzy_search=false):**
    - Works exactly as before
    - Uses standard SQL LIKE search
    
    **With fuzzy search (use_fuzzy_search=true):**
    - Typo-tolerant search
    - Matches similar names (e.g., "Jon" finds "John")
    - Results sorted by relevance
    - Searches across: first_name, last_name, email, designation, biometric_id
    
    **Examples:**
    - GET /users/ → Normal (unchanged)
    - GET /users/?search=john → Normal search (unchanged)
    - GET /users/?use_fuzzy_search=true&fuzzy_query=jon → Fuzzy search (finds "John", "Jonah", etc.)
    - GET /users/?use_fuzzy_search=true&fuzzy_query=johndoe@gmai.com → Fuzzy (finds "johndoe@gmail.com")
    """
    
    # Build base query (EXISTING LOGIC - UNCHANGED)
    query = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department)
    )
    
    # 🔒 Filter by organization (UNCHANGED)
    if current_user.role.name.lower() != "super_admin":
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No organization assigned"
            )
        query = query.filter(User.organization_id == current_user.organization_id)
    
    # Apply existing filters (UNCHANGED)
    if role_id:
        query = query.filter(User.role_id == role_id)
    
    if branch_id:
        query = query.filter(User.branch_id == branch_id)
    
    if inactive is not None:
        query = query.filter(User.inactive == inactive)
    
    # ✅ DECISION POINT: Use fuzzy search OR standard search
    if use_fuzzy_search and fuzzy_query:
        # ✅ NEW PATH: Fuzzy search
        from app.utils.fuzzy_search import apply_fuzzy_search_to_query
        
        # Define fields to search and their weights
        search_fields = ['first_name', 'last_name', 'email', 'designation', 'biometric_id']
        field_weights = {
            'first_name': 2.0,
            'last_name': 2.0,
            'email': 1.5,
            'designation': 1.0,
            'biometric_id': 1.5
        }
        
        # Apply fuzzy search (returns sorted by relevance)
        users = apply_fuzzy_search_to_query(
            base_query=query,
            model_class=User,
            fuzzy_query=fuzzy_query,
            search_fields=search_fields,
            field_weights=field_weights,
            fuzzy_threshold=fuzzy_threshold
        )
        
        # Apply pagination to fuzzy results
        users = users[skip:skip + limit]
    
    elif search:
        # ✅ EXISTING PATH: Standard SQL LIKE search (UNCHANGED)
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
        users = query.offset(skip).limit(limit).all()
    
    else:
        # ✅ DEFAULT PATH: No search, just filters (UNCHANGED)
        users = query.offset(skip).limit(limit).all()
    
    # Map to detailed response (UNCHANGED)
    return [
        UserDetailResponse(
            **user.__dict__,
            role_name=user.role.name if user.role else None,
            branch_name=user.branch.name if user.branch else None,
            organization_name=user.organization.name if user.organization else None,
            department_name=user.department.name if user.department else None
        )
        for user in users
    ]


# ============================================
# GET CURRENT USER PROFILE (UNCHANGED)
# ============================================
@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ UNCHANGED"""
    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department)
    ).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserDetailResponse(
        **user.__dict__,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
        department_name=user.department.name if user.department else None
    )


# ============================================
# GET SINGLE USER BY ID (UNCHANGED)
# ============================================
@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(USERS_MENU_ID))
):
    """✅ UNCHANGED"""
    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if current_user.role.name.lower() != "super_admin":
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users from your organization"
            )
    
    return UserDetailResponse(
        **user.__dict__,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
        department_name=user.department.name if user.department else None
    )


# ============================================
# UPDATE USER (UNCHANGED)
# ============================================
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):
    """✅ UNCHANGED - Original update logic"""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role.name.lower() != "super_admin":
        if db_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update users from your organization"
            )
    
    if payload.role_id and payload.role_id != db_user.role_id:
        new_role = db.query(Role).filter(Role.id == payload.role_id).first()
        if not new_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )
        
        if not validate_role_assignment(current_user, new_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to assign '{new_role.name}' role"
            )
        
        if new_role.name.lower() == "org_admin":
            db_user.is_org_admin = True
        elif db_user.role and db_user.role.name.lower() == "org_admin":
            db_user.is_org_admin = False
    
    if payload.branch_id and payload.branch_id != db_user.branch_id:
        branch = db.query(Branch).filter(
            and_(
                Branch.id == payload.branch_id,
                Branch.organization_id == db_user.organization_id
            )
        ).first()
        
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Branch not found or doesn't belong to the user's organization"
            )
    
    update_data = payload.dict(exclude_unset=True, exclude={"organization_id"})
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db_user.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)


# ============================================
# DELETE USER (UNCHANGED)
# ============================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete_permission(USERS_MENU_ID))
):
    """✅ UNCHANGED"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role.name.lower() != "super_admin":
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete users from your organization"
            )
    
    if user.is_org_admin:
        admin_count = db.query(User).filter(
            and_(
                User.organization_id == user.organization_id,
                User.is_org_admin == True
            )
        ).count()
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last organization admin"
            )
    
    organization_id = user.organization_id
    
    db.delete(user)
    db.commit()
    
    if organization_id:
        TenantLimitsMiddleware.update_user_count(
            organization_id=organization_id,
            db=db,
            increment=False
        )
    
    return None


# ============================================
# ASSIGN SHIFT ROSTER TO ROLE (UNCHANGED)
# ============================================
@router.put("/assign-shift/{role_id}/{shift_roster_id}")
async def assign_shift_to_role(
    role_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):
    """✅ UNCHANGED"""
    if not current_user.organization_id:
        raise HTTPException(status_code=403, detail="No organization assigned")
    
    users = db.query(User).filter(
        and_(
            User.role_id == role_id,
            User.organization_id == current_user.organization_id
        )
    ).all()
    
    if not users:
        raise HTTPException(
            status_code=404,
            detail="No users found with this role in your organization"
        )
    
    for user in users:
        user.shift_roster_id = shift_roster_id
        user.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    
    return {
        "message": "Shift roster assigned to all users of the role",
        "role_id": role_id,
        "shift_roster_id": shift_roster_id,
        "organization_id": current_user.organization_id,
        "total_updated_users": len(users)
    }


# ============================================
# ASSIGN SHIFT ROSTER TO SINGLE USER (UNCHANGED)
# ============================================
@router.patch("/update-shift/{user_id}/{shift_roster_id}")
async def update_user_shift_roster(
    user_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):
    """✅ UNCHANGED"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role.name != "super_admin":
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update users from your organization"
            )
    
    user.shift_roster_id = shift_roster_id
    user.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Shift roster updated for the user",
        "user_id": user_id,
        "shift_roster_id": shift_roster_id
    }


# ============================================
# MAKE USER ORG ADMIN (UNCHANGED)
# ============================================
@router.patch("/{user_id}/make-org-admin")
async def make_user_org_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ UNCHANGED"""
    if not (current_user.is_org_admin or current_user.role.name == "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can promote users"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role.name != "super_admin":
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be in your organization"
            )
    
    user.is_org_admin = True
    user.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User promoted to organization admin",
        "user_id": user_id,
        "is_org_admin": True
    }