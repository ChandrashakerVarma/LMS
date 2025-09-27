# app/routes/branch_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.branch_m import Branch
from app.schema.branch_schema import BranchCreate, BranchResponse, BranchUpdate
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/branches", tags=["branches"])

# Create Branch
@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(branch: BranchCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    existing = db.query(Branch).filter(Branch.name == branch.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Branch with this name already exists")
    new_branch = Branch(**branch.dict())
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch

# List All Branches
@router.get("/", response_model=List[BranchResponse])
def list_branches(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Branch).all()

# Get Branch by ID
@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

# Update Branch
@router.put("/{branch_id}", response_model=BranchResponse)
def update_branch(branch_id: int, payload: BranchUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(branch, key, value)
    db.commit()
    db.refresh(branch)
    return branch

# Delete Branch
@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(branch_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(branch)
    db.commit()
    return {"message": "Branch deleted successfully"}
