from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.department_m import Department
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate, DepartmentResponse

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
def get_all_departments(
    db: Session = Depends(get_db),
    current_user: any = Depends(require_view_permission(MENU_ID))
):
    return db.query(Department).all()


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
