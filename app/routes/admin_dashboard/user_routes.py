from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_
from typing import List, Optional

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
from app.models.salary_structure_m import SalaryStructure
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


# ============================================================
# ROLE VALIDATION HELPER
# ============================================================
def validate_role_assignment(current_user: User, target_role: Role) -> bool:
    current_role = current_user.role.name.lower() if current_user.role else None
    target_role_name = target_role.name.lower()

    if current_role == "super_admin":
        return True

    if current_user.is_org_admin or current_role == "org_admin":
        return target_role_name in ["org_admin", "manager", "employee"]

    if current_role == "manager":
        return target_role_name == "employee"

    return False


# ============================================================
# CREATE USER
# ============================================================
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(USERS_MENU_ID))
):

    # User must belong to an org
    if not current_user.organization_id:
        raise HTTPException(403, "You must belong to an organization to create users")

    # Check org user limit
    await TenantLimitsMiddleware.check_user_limit(
        organization_id=current_user.organization_id,
        db=db
    )

    # Email duplicate check
    existing_user = db.query(User).filter(
        and_(
            User.email == payload.email.lower(),
            User.organization_id == current_user.organization_id
        )
    ).first()

    if existing_user:
        raise HTTPException(400, "Email already exists in your organization")

    # Validate role
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(400, "Invalid role_id")

    if not validate_role_assignment(current_user, role):
        raise HTTPException(403, f"You cannot assign role '{role.name}'")

    # Validate branch belongs to org
    if payload.branch_id:
        branch = db.query(Branch).filter(
            and_(
                Branch.id == payload.branch_id,
                Branch.organization_id == current_user.organization_id
            )
        ).first()

        if not branch:
            raise HTTPException(400, "Branch does not belong to your organization")

    # SALARY STRUCTURE VALIDATION (✔ organization_id removed)
    if payload.salary_structure_id:
        structure = db.query(SalaryStructure).filter(
            SalaryStructure.id == payload.salary_structure_id
        ).first()

        if not structure:
            raise HTTPException(400, "Invalid salary_structure_id")

    # Prepare user data
    user_data = payload.dict(exclude={"password"})
    user_data["hashed_password"] = hash_password(payload.password)
    user_data["organization_id"] = current_user.organization_id
    user_data["created_by"] = f"{current_user.first_name} {current_user.last_name}"

    # Set org admin flag properly
    user_data["is_org_admin"] = (
        role.name.lower() == "org_admin" and
        (current_user.is_org_admin or current_user.role.name.lower() == "super_admin")
    )

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


# ============================================================
# AVAILABLE ROLES TO ASSIGN
# ============================================================
@router.get("/available-roles")
async def get_available_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    current_role = current_user.role.name.lower() if current_user.role else None

    if current_role == "super_admin":
        allowed = ["super_admin", "org_admin", "manager", "employee"]
    elif current_user.is_org_admin or current_role == "org_admin":
        allowed = ["org_admin", "manager", "employee"]
    elif current_role == "manager":
        allowed = ["employee"]
    else:
        allowed = []

    if not allowed:
        return []

    roles = db.query(Role).filter(Role.name.in_(allowed)).all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "display_name": r.name.replace("_", " ").title()
        }
        for r in roles
    ]


# ============================================================
# GET ALL USERS
# ============================================================
@router.get("/", response_model=List[UserDetailResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    inactive: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(USERS_MENU_ID))
):

    query = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department),
        selectinload(User.salary_structure)
    )

    if current_user.role.name.lower() != "super_admin":
        query = query.filter(User.organization_id == current_user.organization_id)

    if role_id:
        query = query.filter(User.role_id == role_id)
    if branch_id:
        query = query.filter(User.branch_id == branch_id)
    if inactive is not None:
        query = query.filter(User.inactive == inactive)

    if search:
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    users = query.offset(skip).limit(limit).all()

    return [
        UserDetailResponse(
            **u.__dict__,
            role_name=u.role.name if u.role else None,
            branch_name=u.branch.name if u.branch else None,
            organization_name=u.organization.name if u.organization else None,
            department_name=u.department.name if u.department else None,
            salary_structure_name=u.salary_structure.name if u.salary_structure else None
        )
        for u in users
    ]


# ============================================================
# GET CURRENT USER PROFILE
# ============================================================
@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department),
        selectinload(User.salary_structure)
    ).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(404, "User not found")

    return UserDetailResponse(
        **user.__dict__,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
        department_name=user.department.name if user.department else None,
        salary_structure_name=user.salary_structure.name if user.salary_structure else None
    )


# ============================================================
# GET USER BY ID
# ============================================================
@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(USERS_MENU_ID))
):

    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department),
        selectinload(User.salary_structure)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    if current_user.role.name.lower() != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")

    return UserDetailResponse(
        **user.__dict__,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
        department_name=user.department.name if user.department else None,
        salary_structure_name=user.salary_structure.name if user.salary_structure else None
    )


# ============================================================
# UPDATE USER
# ============================================================
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(404, "User not found")

    if current_user.role.name.lower() != "super_admin" and \
            db_user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")

    # ROLE UPDATE
    if payload.role_id and payload.role_id != db_user.role_id:
        new_role = db.query(Role).filter(Role.id == payload.role_id).first()
        if not new_role:
            raise HTTPException(400, "Invalid role_id")

        if not validate_role_assignment(current_user, new_role):
            raise HTTPException(403, "You cannot assign this role")

        db_user.is_org_admin = new_role.name.lower() == "org_admin"

    # BRANCH UPDATE
    if payload.branch_id and payload.branch_id != db_user.branch_id:
        branch = db.query(Branch).filter(
            and_(
                Branch.id == payload.branch_id,
                Branch.organization_id == db_user.organization_id
            )
        ).first()

        if not branch:
            raise HTTPException(400, "Branch does not belong to organization")

    # SALARY STRUCTURE UPDATE (✔ organization check removed)
    if payload.salary_structure_id:
        structure = db.query(SalaryStructure).filter(
            SalaryStructure.id == payload.salary_structure_id
        ).first()

        if not structure:
            raise HTTPException(400, "Invalid salary_structure_id")

        db_user.salary_structure_id = payload.salary_structure_id

    # UPDATE OTHER FIELDS
    update_data = payload.dict(exclude_unset=True, exclude={"organization_id"})
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db_user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()
    db.refresh(db_user)

    return UserResponse.model_validate(db_user)


# ============================================================
# DELETE USER
# ============================================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete_permission(USERS_MENU_ID))
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    if current_user.role.name.lower() != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")

    if user.is_org_admin:
        count = db.query(User).filter(
            and_(
                User.organization_id == user.organization_id,
                User.is_org_admin == True
            )
        ).count()

        if count <= 1:
            raise HTTPException(400, "Cannot delete last org admin")

    org_id = user.organization_id

    db.delete(user)
    db.commit()

    TenantLimitsMiddleware.update_user_count(
        organization_id=org_id,
        db=db,
        increment=False
    )

    return None


# ============================================================
# ASSIGN SHIFT ROSTER TO ROLE
# ============================================================
@router.put("/assign-shift/{role_id}/{shift_roster_id}")
async def assign_shift_to_role(
    role_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):

    if not current_user.organization_id:
        raise HTTPException(403, "No organization assigned")

    users = db.query(User).filter(
        and_(
            User.role_id == role_id,
            User.organization_id == current_user.organization_id
        )
    ).all()

    if not users:
        raise HTTPException(404, "No users found")

    for user in users:
        user.shift_roster_id = shift_roster_id
        user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()

    return {
        "message": "Shift roster assigned",
        "role_id": role_id,
        "shift_roster_id": shift_roster_id,
        "updated_users": len(users)
    }


# ============================================================
# ASSIGN SHIFT ROSTER TO SINGLE USER
# ============================================================
@router.patch("/update-shift/{user_id}/{shift_roster_id}")
async def update_user_shift_roster(
    user_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if current_user.role.name.lower() != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")

    user.shift_roster_id = shift_roster_id
    user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()
    db.refresh(user)

    return {
        "message": "Shift roster updated",
        "user_id": user_id,
        "shift_roster_id": shift_roster_id
    }


# ============================================================
# MAKE USER ORG ADMIN
# ============================================================
@router.patch("/{user_id}/make-org-admin")
async def make_user_org_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not (current_user.is_org_admin or current_user.role.name == "super_admin"):
        raise HTTPException(403, "Only org admins can promote users")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if current_user.role.name != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Target must be in your organization")

    user.is_org_admin = True
    user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()
    db.refresh(user)

    return {
        "message": "User promoted to org admin",
        "user_id": user_id
    }
