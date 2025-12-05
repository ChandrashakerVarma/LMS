from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.salary_structure_m import SalaryStructure
from app.schema.salary_structure_schema import (
    SalaryStructureCreate,
    SalaryStructureUpdate,
    SalaryStructureResponse,
)
from app.dependencies import require_org_admin
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/salary-structures", tags=["Salary Structure"])

MENU_ID = 47


# ------------------ Create Salary Structure ------------------
@router.post(
    "/", 
    response_model=SalaryStructureResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_salary_structure(
    data: SalaryStructureCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_org_admin),
):
    total_annual = (
        data.basic_salary_annual
        + (data.allowances_annual or 0)
        + (data.bonus_annual or 0)
        - (data.deductions_annual or 0)
    )

    new_salary_structure = SalaryStructure(
        **data.dict(),
        total_annual=total_annual,
        created_by=current_user.first_name
    )

    db.add(new_salary_structure)
    db.commit()
    db.refresh(new_salary_structure)
    return new_salary_structure


# ------------------ Get All Salary Structures ------------------
@router.get(
    "/", 
    response_model=List[SalaryStructureResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_salary_structures(db: Session = Depends(get_db)):
    return db.query(SalaryStructure).all()


# ------------------ Get Salary Structure by ID ------------------
@router.get(
    "/{salary_structure_id}", 
    response_model=SalaryStructureResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_salary_structure(salary_structure_id: int, db: Session = Depends(get_db)):
    structure = db.query(SalaryStructure).filter(SalaryStructure.id == salary_structure_id).first()
    if not structure:
        raise HTTPException(status_code=404, detail="Salary Structure not found")
    return structure


# ------------------ Update Salary Structure ------------------
@router.put(
    "/{salary_structure_id}", 
    response_model=SalaryStructureResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_salary_structure(
    salary_structure_id: int,
    data: SalaryStructureUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_org_admin),
):
    structure = db.query(SalaryStructure).filter(SalaryStructure.id == salary_structure_id).first()
    if not structure:
        raise HTTPException(status_code=404, detail="Salary Structure not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(structure, key, value)

    structure.total_annual = (
        (structure.basic_salary_annual or 0)
        + (structure.allowances_annual or 0)
        + (structure.bonus_annual or 0)
        - (structure.deductions_annual or 0)
    )

    structure.modified_by = current_user.first_name

    db.commit()
    db.refresh(structure)
    return structure


# ------------------ Delete Salary Structure ------------------
@router.delete(
    "/{salary_structure_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_salary_structure(
    salary_structure_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_org_admin),
):
    structure = db.query(SalaryStructure).filter(SalaryStructure.id == salary_structure_id).first()
    if not structure:
        raise HTTPException(status_code=404, detail="Salary Structure not found")

    db.delete(structure)
    db.commit()
    return {"message": "Salary Structure deleted successfully"}
