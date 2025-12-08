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

from app.schemas.organization_schema import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationAdminUpdate,
    OrganizationResponse,
    OrganizationDetailResponse,
    OrganizationStatsResponse,
)

from app.dependencies import get_current_user
from app.middleware.tenant_limits import TenantLimitsMiddleware

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])
MENU_ID = 7


# ---------------------------------------------------------
# CREATE ORGANIZATION
# ---------------------------------------------------------
@router.post("/", response_model=OrganizationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(MENU_ID))
):

    existing = db.query(Organization).filter(Organization.name == org.name).first()
    if existing:
        raise HTTPException(400, "Organization already exists")

    if org.plan_id:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == org.plan_id).first()
        if not plan:
            raise HTTPException(404, "Subscription plan not found")
    else:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "Basic").first()
        if not plan:
            raise HTTPException(500, "Default plan is not configured")

    new_org = Organization(
        name=org.name,
        description=org.description,
        plan_id=plan.id,
        subscription_status="trial",
        subscription_start_date=date.today(),
        subscription_end_date=date.today() + timedelta(days=30),
        branch_limit=plan.branch_limit,
        user_limit=plan.user_limit,
        storage_limit_mb=plan.storage_limit_mb,
        current_branches=0,
        current_users=0,
        current_storage_mb=0,
        contact_email=org.contact_email,
        contact_phone=org.contact_phone,
        created_by=current_user.email,
    )

    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org


# ---------------------------------------------------------
# LIST ORGS
# ---------------------------------------------------------
@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    status_filter: str = None,
    search: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):

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
# MY ORG
# ---------------------------------------------------------
@router.get("/me", response_model=OrganizationDetailResponse)
async def get_my_org(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not current_user.organization_id:
        raise HTTPException(404, "No organization assigned")

    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    return org


# ---------------------------------------------------------
# MY ORG STATS
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

    days_left = (org.subscription_end_date - date.today()).days if org.subscription_end_date else None

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
# GET ORG BY ID
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
# UPDATE ORG
# ---------------------------------------------------------
@router.put("/{org_id}", response_model=OrganizationDetailResponse)
async def update_org(
    org_id: int,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    if current_user.role.name != "super_admin":
        if current_user.organization_id != org_id:
            raise HTTPException(403, "You can only update your organization")

    for k, v in payload.dict(exclude_unset=True).items():
        setattr(org, k, v)

    org.modified_by = current_user.email
    db.commit()
    db.refresh(org)
    return org


# ---------------------------------------------------------
# ADMIN UPDATE (SUPER ADMIN)
# ---------------------------------------------------------
@router.put("/{org_id}/admin", response_model=OrganizationDetailResponse)
async def admin_update_org(
    org_id: int,
    payload: OrganizationAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):

    if current_user.role.name != "super_admin":
        raise HTTPException(403, "Only super admin can modify organization settings")

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
# DELETE ORG
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
    return None


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------
@router.get("/{org_id}/health")
async def org_health(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        org = await TenantLimitsMiddleware.check_organization_status(org_id, db)
        return {
            "status": "healthy",
            "subscription_status": org.subscription_status,
            "subscription_expires": org.subscription_end_date,
            "days_remaining": (org.subscription_end_date - date.today()).days if org.subscription_end_date else None,
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
    except HTTPException as e:
        return {
            "status": "unhealthy",
            "error": e.detail
        }
