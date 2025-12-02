from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.department_m import Department
from app.schema.department_schema import DepartmentCreate, DepartmentUpdate, DepartmentResponse

from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/departments", tags=["Departments"])

MENU_ID = 9   # Department Module ID


# ➕ Create Department
@router.post("/", response_model=DepartmentResponse)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: any = Depends(require_create_permission(MENU_ID))
):
    new_dept = Department(
        name=department.name,
        code=department.code,
        description=department.description,
        status=department.status,
        created_by=current_user.first_name
    )

    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept


# 📋 Get All Departments
@router.get("/", response_model=List[DepartmentResponse])
async def get_all_departments(
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
    Get all departments with OPTIONAL fuzzy search
    
    Searches across: name, code, description
    """
    
    query = db.query(Department)
    
    # Your existing filters here
    
    if use_fuzzy_search and fuzzy_query:
        from app.utils.fuzzy_search import apply_fuzzy_search_to_query
        
        search_fields = ['name', 'code', 'description']
        field_weights = {
            'name': 2.5,
            'code': 2.0,
            'description': 1.0
        }
        
        departments = apply_fuzzy_search_to_query(
            base_query=query,
            model_class=Department,
            fuzzy_query=fuzzy_query,
            search_fields=search_fields,
            field_weights=field_weights,
            fuzzy_threshold=fuzzy_threshold
        )
        
        departments = departments[skip:skip + limit]
    else:
        departments = query.offset(skip).limit(limit).all()
    
    return departments

# 🔍 Get Department by ID
@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: any = Depends(require_view_permission(MENU_ID))
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


# ✏️ Update Department
@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    update_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: any = Depends(require_edit_permission(MENU_ID))
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(dept, key, value)

    dept.modified_by = current_user.first_name

    db.commit()
    db.refresh(dept)
    return dept


# ❌ Delete Department
@router.delete("/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: any = Depends(require_delete_permission(MENU_ID))
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    db.delete(dept)
    db.commit()
    return {"message": "Department deleted successfully"}
