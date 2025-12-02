from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.branch_m import Branch
from app.schema.branch_schema import BranchCreate, BranchResponse, BranchUpdate

from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/branches", tags=["branches"])

# ✅ Correct Menu ID from your Seeder
BRANCHES_MENU_ID = 8


# ----------------------
# Create Branch
# ----------------------
@router.post(
    "/", 
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(BRANCHES_MENU_ID))]
)
def create_branch(branch: BranchCreate, db: Session = Depends(get_db)):
    
    existing = db.query(Branch).filter(Branch.name == branch.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Branch with this name already exists")
    
    new_branch = Branch(**branch.dict())
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)

    return new_branch


# ----------------------
# List All Branches
# ----------------------
@router.get("/", response_model=List[BranchResponse])
async def get_all_branches(
    # ✅ NEW: Fuzzy search parameters
    use_fuzzy_search: bool = Query(False, description="Enable fuzzy search"),
    fuzzy_query: Optional[str] = Query(None, description="Fuzzy search query"),
    fuzzy_threshold: int = Query(70, ge=50, le=100),
    
    # Your existing parameters
    skip: int = 0,
    limit: int = 100,
    
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all branches with OPTIONAL fuzzy search
    
    Searches across: name, address
    """
    
    query = db.query(Branch)
    
    # Filter by organization (keep your existing logic)
    if hasattr(current_user, 'organization_id') and current_user.organization_id:
        query = query.filter(Branch.organization_id == current_user.organization_id)
    
    if use_fuzzy_search and fuzzy_query:
        from app.utils.fuzzy_search import apply_fuzzy_search_to_query
        
        search_fields = ['name', 'address']
        field_weights = {
            'name': 2.5,
            'address': 1.5
        }
        
        branches = apply_fuzzy_search_to_query(
            base_query=query,
            model_class=Branch,
            fuzzy_query=fuzzy_query,
            search_fields=search_fields,
            field_weights=field_weights,
            fuzzy_threshold=fuzzy_threshold
        )
        
        branches = branches[skip:skip + limit]
    else:
        branches = query.offset(skip).limit(limit).all()
    
    return branches
# ----------------------
# Get Branch by ID
# ----------------------
@router.get(
    "/{branch_id}", 
    response_model=BranchResponse,
    dependencies=[Depends(require_view_permission(BRANCHES_MENU_ID))]
)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    return branch


# ----------------------
# Update Branch
# ----------------------
@router.put(
    "/{branch_id}", 
    response_model=BranchResponse,
    dependencies=[Depends(require_edit_permission(BRANCHES_MENU_ID))]
)
def update_branch(branch_id: int, payload: BranchUpdate, db: Session = Depends(get_db)):

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(branch, key, value)

    db.commit()
    db.refresh(branch)

    return branch


# ----------------------
# Delete Branch
# ----------------------
@router.delete(
    "/{branch_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(BRANCHES_MENU_ID))]
)
def delete_branch(branch_id: int, db: Session = Depends(get_db)):

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    db.delete(branch)
    db.commit()

    return {"message": "Branch deleted successfully"}
