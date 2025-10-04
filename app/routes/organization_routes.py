# app/routes/organization_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.organization import Organization
from app.models.branch_m import Branch 
from app.schema.organization_schema import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    existing = db.query(Organization).filter(Organization.name == org.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")

    new_org = Organization(name=org.name, description=org.description)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    # Associate branches if provided
    if org.branch_ids:
        branches = db.query(Branch).filter(Branch.id.in_(org.branch_ids)).all()
        new_org.branches = branches
        db.commit()
        db.refresh(new_org)

    return new_org

@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    orgs = db.query(Organization).all()
    return orgs

@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(org_id: int, payload: OrganizationUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    update_data = payload.dict(exclude_unset=True)
    
    # Update basic fields
    for key in ["name", "description"]:
        if key in update_data:
            setattr(org, key, update_data[key])

    # Update branches if provided
    if "branch_ids" in update_data:
        branches = db.query(Branch).filter(Branch.id.in_(update_data["branch_ids"])).all()
        org.branches = branches

    db.commit()
    db.refresh(org)
    return org

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    db.delete(org)
    db.commit()
    return {"message": "Organization deleted successfully"}