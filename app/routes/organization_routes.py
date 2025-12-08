from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta

from app.database import get_db
from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.user_m import User
from app.models.branch_m import Branch
from app.models.course_m import Course
<<<<<<< HEAD

from app.schemas.organization_schema import (
=======
from app.schema.organization_schema import (
>>>>>>> origin/main
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationAdminUpdate,
    OrganizationResponse,
    OrganizationDetailResponse,
    OrganizationStatsResponse,
)
<<<<<<< HEAD
=======
from app.dependencies import get_current_user
from app.middleware.tenant_limits import TenantLimitsMiddleware
>>>>>>> origin/main

from app.dependencies import get_current_user
from app.middleware.tenant_limits import TenantLimitsMiddleware

# Permission checks
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])

MENU_ID = 7   # Organizations Menu ID


<<<<<<< HEAD
# ---------------------------------------------------------
# CREATE ORGANIZATION (Super Admin Only)
# ---------------------------------------------------------
=======
# 🔹 Create Organization (ADMIN/SUPER-ADMIN ONLY)
>>>>>>> origin/main
@router.post("/", response_model=OrganizationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(MENU_ID))
):
<<<<<<< HEAD
    # Check name uniqueness
    existing = db.query(Organization).filter(Organization.name == org.name).first()
    if existing:
        raise HTTPException(400, "Organization already exists")

    # Plan selection
    if org.plan_id:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == org.plan_id).first()
        if not plan:
            raise HTTPException(404, "Subscription plan not found")
    else:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "Basic").first()
        if not plan:
            raise HTTPException(500, "Default plan is not configured")

    # Create new org
=======
    """
    ✅ Create a new organization with automatic plan assignment
    Only accessible by Super Admin (for manual organization creation)
    """
    
    # Check if organization name already exists
    existing = db.query(Organization).filter(Organization.name == org.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this name already exists"
        )

    # Get plan (or use default)
    if org.plan_id:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == org.plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
    else:
        # Assign default "Basic" plan
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "Basic").first()
        if not plan:
            raise HTTPException(status_code=500, detail="Default plan not configured")

    # Create organization with plan limits
>>>>>>> origin/main
    new_org = Organization(
        name=org.name,
        description=org.description,
        plan_id=plan.id,
<<<<<<< HEAD

        subscription_status="trial",
        subscription_start_date=date.today(),
        subscription_end_date=date.today() + timedelta(days=30),

        # Limits from plan
        branch_limit=plan.branch_limit,
        user_limit=plan.user_limit,
        storage_limit_mb=plan.storage_limit_mb,

        # Usage
        current_branches=0,
        current_users=0,
        current_storage_mb=0,

        # Contact
        contact_email=org.contact_email,
        contact_phone=org.contact_phone,

        created_by=current_user.email
    )

=======
        subscription_status="trial",  # Start with trial
        subscription_start_date=date.today(),
        subscription_end_date=date.today() + timedelta(days=30),  # 30-day trial
        
        # Set limits from plan
        branch_limit=plan.branch_limit,
        user_limit=plan.user_limit,
        storage_limit_mb=plan.storage_limit_mb,
        
        # Initialize counters
        current_branches=0,
        current_users=0,
        current_storage_mb=0,
        
        # Contact info
        contact_email=org.contact_email,
        contact_phone=org.contact_phone,
        
        is_active=True,
        created_by=f"{current_user.first_name} {current_user.last_name}"
    )
    
>>>>>>> origin/main
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    return new_org


<<<<<<< HEAD
# ---------------------------------------------------------
# LIST ORGANIZATIONS
# ---------------------------------------------------------
@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    status_filter: str = None,
=======
# 🔹 Get All Organizations (with filters)
@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    status_filter: str = None,  # active, trial, expired, suspended
>>>>>>> origin/main
    search: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
<<<<<<< HEAD
    query = db.query(Organization)

    if current_user.role.name != "super_admin":
        if not current_user.organization_id:
            raise HTTPException(403, "You don't belong to any organization")
        query = query.filter(Organization.id == current_user.organization_id)

    if status_filter:
        query = query.filter(Organization.subscription_status == status_filter)

    if search:
        query = query.filter(Organization.name.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()


# ---------------------------------------------------------
# GET MY ORGANIZATION
# ---------------------------------------------------------
@router.get("/me", response_model=OrganizationDetailResponse)
async def get_my_org(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(404, "No organization assigned")

    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()

=======
    """
    ✅ Get all organizations with optional filters
    Super Admin can see all, Org Admin sees only their org
    """
    
    query = db.query(Organization)
    
    # 🔒 If user is not super admin, show only their organization
    if current_user.role.name != "super_admin":
        if not current_user.organization_id:
            raise HTTPException(status_code=403, detail="No organization assigned")
        query = query.filter(Organization.id == current_user.organization_id)
    
    # Apply filters
    if status_filter:
        query = query.filter(Organization.subscription_status == status_filter)
    
    if search:
        query = query.filter(Organization.name.ilike(f"%{search}%"))
    
    organizations = query.offset(skip).limit(limit).all()
    return organizations


# 🔹 Get Current User's Organization
@router.get("/me", response_model=OrganizationDetailResponse)
async def get_my_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Get details of the current user's organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned to this user"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return org


# 🔹 Get Organization Statistics
@router.get("/me/stats", response_model=OrganizationStatsResponse)
async def get_organization_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Get usage statistics for current user's organization
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=404, detail="No organization assigned")
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Count resources
    total_branches = db.query(func.count(Branch.id)).filter(
        Branch.organization_id == org.id
    ).scalar()
    
    total_users = db.query(func.count(User.id)).filter(
        User.organization_id == org.id
    ).scalar()
    
    total_courses = db.query(func.count(Course.id)).filter(
        Course.organization_id == org.id
    ).scalar()
    
    # Calculate days until expiry
    days_until_expiry = None
    if org.subscription_end_date:
        days_until_expiry = (org.subscription_end_date - date.today()).days
    
    return OrganizationStatsResponse(
        organization_id=org.id,
        organization_name=org.name,
        total_branches=total_branches,
        total_users=total_users,
        total_courses=total_courses,
        storage_used_mb=org.current_storage_mb,
        storage_limit_mb=org.storage_limit_mb,
        subscription_status=org.subscription_status,
        days_until_expiry=days_until_expiry,
        plan_name=org.plan.name if org.plan else None
    )


# 🔹 Get Single Organization (by ID)
@router.get("/{org_id}", response_model=OrganizationDetailResponse)
async def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    """
    ✅ Get organization details by ID
    """
    
    # 🔒 Check access permissions
    if current_user.role.name != "super_admin":
        if current_user.organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own organization"
            )
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
>>>>>>> origin/main
    if not org:
        raise HTTPException(404, "Organization not found")

    return org


<<<<<<< HEAD
# ---------------------------------------------------------
# GET MY ORGANIZATION STATS
# ---------------------------------------------------------
@router.get("/me/stats", response_model=OrganizationStatsResponse)
async def get_org_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(404, "No organization assigned")

    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    total_branches = db.query(func.count(Branch.id)).filter(Branch.organization_id == org.id).scalar()
    total_users = db.query(func.count(User.id)).filter(User.organization_id == org.id).scalar()
    total_courses = db.query(func.count(Course.id)).filter(Course.organization_id == org.id).scalar()

    days_left = None
    if org.subscription_end_date:
        days_left = (org.subscription_end_date - date.today()).days

    return OrganizationStatsResponse(
        organization_id=org.id,
        organization_name=org.name,
        total_branches=total_branches,
        total_users=total_users,
        total_courses=total_courses,
        storage_used_mb=org.current_storage_mb,
        storage_limit_mb=org.storage_limit_mb,
        subscription_status=org.subscription_status,
        days_until_expiry=days_left,
        plan_name=org.plan.name if org.plan else None
    )


# ---------------------------------------------------------
# GET ORGANIZATION BY ID
# ---------------------------------------------------------
@router.get("/{org_id}", response_model=OrganizationDetailResponse)
async def get_org(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    if current_user.role.name != "super_admin":
        if current_user.organization_id != org_id:
            raise HTTPException(403, "You can only access your organization")

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    return org


# ---------------------------------------------------------
# UPDATE ORGANIZATION (ORG ADMIN)
# ---------------------------------------------------------
@router.put("/{org_id}", response_model=OrganizationDetailResponse)
async def update_org(
=======
# 🔹 Update Organization (ORG ADMIN)
@router.put("/{org_id}", response_model=OrganizationDetailResponse)
async def update_organization(
>>>>>>> origin/main
    org_id: int,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    """
    ✅ Update organization details (limited fields for org admin)
    """
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
<<<<<<< HEAD
        raise HTTPException(404, "Organization not found")

    if current_user.role.name != "super_admin":
        if current_user.organization_id != org_id:
            raise HTTPException(403, "You can only update your own organization")
=======
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # 🔒 Check permissions
    if current_user.role.name != "super_admin":
        if current_user.organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own organization"
            )
>>>>>>> origin/main

    # Update allowed fields
    update_data = payload.dict(exclude_unset=True)
<<<<<<< HEAD
    for k, v in update_data.items():
        setattr(org, k, v)

    org.modified_by = current_user.email

=======
    for key, value in update_data.items():
        setattr(org, key, value)
    
    org.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
>>>>>>> origin/main
    db.commit()
    db.refresh(org)
    return org


<<<<<<< HEAD
# ---------------------------------------------------------
# ADMIN UPDATE (SUPER ADMIN ONLY)
# ---------------------------------------------------------
@router.put("/{org_id}/admin", response_model=OrganizationDetailResponse)
async def admin_update_org(
=======
# 🔹 Update Organization Admin Settings (SUPER ADMIN ONLY)
@router.put("/{org_id}/admin", response_model=OrganizationDetailResponse)
async def admin_update_organization(
    org_id: int,
    payload: OrganizationAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    """
    ✅ Update organization settings including plan, limits, status (Super Admin only)
    """
    
    # 🔒 Only super admin can use this endpoint
    if current_user.role.name != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can modify these settings"
        )
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # If plan is being changed, update limits
    if payload.plan_id:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == payload.plan_id
        ).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        
        # Auto-update limits from new plan (unless manually overridden)
        if payload.branch_limit is None:
            org.branch_limit = plan.branch_limit
        if payload.user_limit is None:
            org.user_limit = plan.user_limit
        if payload.storage_limit_mb is None:
            org.storage_limit_mb = plan.storage_limit_mb
    
    # Update all provided fields
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)
    
    org.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    db.refresh(org)
    return org


# 🔹 Delete Organization (SUPER ADMIN ONLY)
@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
>>>>>>> origin/main
    org_id: int,
    payload: OrganizationAdminUpdate,
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    if current_user.role.name != "super_admin":
        raise HTTPException(403, "Only super admin can modify organization settings")

=======
    current_user: User = Depends(require_delete_permission(MENU_ID))
):
    """
    ✅ Delete organization (Super Admin only)
    ⚠️ This will cascade delete all branches, users, courses, etc.
    """
    
    # 🔒 Only super admin can delete organizations
    if current_user.role.name != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can delete organizations"
        )
    
>>>>>>> origin/main
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    if payload.plan_id:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == payload.plan_id).first()
        if not plan:
            raise HTTPException(404, "Subscription plan not found")

        if payload.branch_limit is None:
            org.branch_limit = plan.branch_limit
        if payload.user_limit is None:
            org.user_limit = plan.user_limit
        if payload.storage_limit_mb is None:
            org.storage_limit_mb = plan.storage_limit_mb

    for k, v in payload.dict(exclude_unset=True).items():
        setattr(org, k, v)

    org.modified_by = current_user.email

    db.commit()
    db.refresh(org)
    return org


# ---------------------------------------------------------
# DELETE ORGANIZATION (SUPER ADMIN ONLY)
# ---------------------------------------------------------
@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete_permission(MENU_ID))
):
    if current_user.role.name != "super_admin":
        raise HTTPException(403, "Only super admin can delete organizations")

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    db.delete(org)
    db.commit()
<<<<<<< HEAD
    return None


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------
@router.get("/{org_id}/health")
async def org_health(
=======
    
    return None


# 🔹 Check Organization Health
@router.get("/{org_id}/health")
async def check_organization_health(
>>>>>>> origin/main
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
<<<<<<< HEAD
    try:
        org = await TenantLimitsMiddleware.check_organization_status(org_id, db)

=======
    """
    ✅ Check organization subscription and limits status
    """
    
    try:
        # Use middleware to check organization status
        org = await TenantLimitsMiddleware.check_organization_status(org_id, db)
        
>>>>>>> origin/main
        return {
            "status": "healthy",
            "subscription_status": org.subscription_status,
            "subscription_expires": org.subscription_end_date,
<<<<<<< HEAD
            "days_remaining":
                (org.subscription_end_date - date.today()).days
                if org.subscription_end_date else None,
            "limits": {
                "branches": {
                    "used": org.current_branches,
                    "limit": org.branch_limit
                },
                "users": {
                    "used": org.current_users,
                    "limit": org.user_limit
                },
                "storage_mb": {
                    "used": org.current_storage_mb,
                    "limit": org.storage_limit_mb
                }
            }
        }

=======
            "days_remaining": (org.subscription_end_date - date.today()).days if org.subscription_end_date else None,
            "limits": {
                "branches": {
                    "used": org.current_branches,
                    "limit": org.branch_limit,
                    "remaining": org.branch_limit - org.current_branches
                },
                "users": {
                    "used": org.current_users,
                    "limit": org.user_limit,
                    "remaining": org.user_limit - org.current_users
                },
                "storage_mb": {
                    "used": org.current_storage_mb,
                    "limit": org.storage_limit_mb,
                    "remaining": org.storage_limit_mb - org.current_storage_mb
                }
            }
        }
>>>>>>> origin/main
    except HTTPException as e:
        return {
            "status": "unhealthy",
            "error": e.detail
<<<<<<< HEAD
        }
=======
        }
>>>>>>> origin/main
