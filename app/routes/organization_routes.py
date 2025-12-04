# app/routes/organization_routes.py
from fastapi import APIRouter,Depends,HTTPException,status,UploadFile,File,Form
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.organization_m import Organization
from app.schema.organization_schema import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse
)
from app.dependencies import get_current_user
from app.utils.s3_company_logo import upload_organization_logo

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])
MENU_ID = 7

# ---------------------
# CREATE ORGANIZATION
# -------------------------
@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    name: str = Form(...),
    description: str = Form(None),
    organization_logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_create_permission(MENU_ID))
):
    existing = db.query(Organization).filter(Organization.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")

    logo_url = None
    if organization_logo:
        file_bytes = await organization_logo.read()
        logo_url = upload_organization_logo(file_bytes, organization_logo.filename)

    new_org = Organization(
        name=name,
        description=description,
        organization_logo=logo_url
    )

    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org
 
# ----------------------
# LIST ALL ORGANIZATIONS
# -------------------------------
@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
    current_user=Depends(require_view_permission(MENU_ID))
):
    return db.query(Organization).all()

# ----------------------------------
# GET SINGLE ORGANIZATION
# -----------------------------------

@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_view_permission(MENU_ID))
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

# -----------------------
# UPDATE
# --------------------------
@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: int,
    name: str = Form(None),
    description: str = Form(None),
    organization_logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_edit_permission(MENU_ID))
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if name:
        org.name = name
    if description:
        org.description = description

    if organization_logo:
        file_bytes = await organization_logo.read()
        org.organization_logo = upload_organization_logo(file_bytes, organization_logo.filename)

    db.commit()
    db.refresh(org)
    return org

# ----------------------------
# DELETE
# ---------------------------
@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_delete_permission(MENU_ID))
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    db.delete(org)
    db.commit()
    return {"message": "Organization deleted successfully"}
