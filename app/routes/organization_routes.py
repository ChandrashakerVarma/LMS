from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.organization_m import Organization
from app.Schema.organization_schema import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)
from app.dependencies import get_current_user

# ---- Permission Imports ----
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])

MENU_ID = 7   # Organizations Menu


# 🔹 Create Organization
@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_create_permission(MENU_ID))
):
    existing = db.query(Organization).filter(Organization.name == org.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")

    new_org = Organization(
        name=org.name,
        description=org.description
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    return new_org


# 🔹 Get All Organizations
@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    return db.query(Organization).all()


# 🔹 Get Single Organization
@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return org


# 🔹 Update Organization
@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: int,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_edit_permission(MENU_ID))
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)

    db.commit()
    db.refresh(org)
    return org


# 🔹 Delete Organization
@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_delete_permission(MENU_ID))
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    db.delete(org)
    db.commit()
    return {"message": "Organization deleted successfully"}
