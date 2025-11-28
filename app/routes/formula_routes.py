from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.formula_m import Formula
from app.Schema.formula_schema import FormulaCreate, FormulaUpdate, FormulaResponse

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/formulas", tags=["Formulas"])

MENU_ID = 48   # Formula Module


# ➕ CREATE FORMULA
@router.post("/", response_model=FormulaResponse, status_code=status.HTTP_201_CREATED)
def create_formula(
    payload: FormulaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_create_permission(MENU_ID))
):
    # Check if component code already exists
    existing = db.query(Formula).filter(Formula.component_code == payload.component_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Formula with this code already exists")

    formula = Formula(
        component_code=payload.component_code,
        component_name=payload.component_name,
        formula_expression=payload.formula_expression,
        formula_type=payload.formula_type,
        is_active=payload.is_active,
        description=payload.description,
        salary_structure_id=payload.salary_structure_id,
        created_by=current_user.first_name     # Set on create
    )

    db.add(formula)
    db.commit()
    db.refresh(formula)
    return formula


# 📋 READ ALL FORMULAS
@router.get("/", response_model=List[FormulaResponse])
def list_formulas(
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    return db.query(Formula).all()


# 🔍 READ FORMULA BY ID
@router.get("/{formula_id}", response_model=FormulaResponse)
def get_formula(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")

    return formula


# ✏️ UPDATE FORMULA
@router.put("/{formula_id}", response_model=FormulaResponse)
def update_formula(
    formula_id: int,
    payload: FormulaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_edit_permission(MENU_ID))
):
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")

    # Apply updates
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(formula, key, value)

    formula.modified_by = current_user.first_name     # Set on update

    db.commit()
    db.refresh(formula)
    return formula


# ❌ DELETE FORMULA
@router.delete("/{formula_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_formula(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_delete_permission(MENU_ID))
):
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")

    db.delete(formula)
    db.commit()
    return {"message": "Formula deleted successfully"}
