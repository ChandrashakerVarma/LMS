from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.formula_m import Formula
from app.schema.formula_schema import FormulaCreate, FormulaUpdate, FormulaResponse
from app.dependencies import require_admin

router = APIRouter(prefix="/formulas", tags=["Formulas"])

# CREATE
@router.post("/", response_model=FormulaResponse, status_code=status.HTTP_201_CREATED)
def create_formula(payload: FormulaCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    existing = db.query(Formula).filter(Formula.component_code == payload.component_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Formula with this code already exists")
    formula = Formula(**payload.dict())
    db.add(formula)
    db.commit()
    db.refresh(formula)
    return formula

# READ ALL
@router.get("/", response_model=List[FormulaResponse])
def list_formulas(db: Session = Depends(get_db)):
    return db.query(Formula).all()

# READ BY ID
@router.get("/{formula_id}", response_model=FormulaResponse)
def get_formula(formula_id: int, db: Session = Depends(get_db)):
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    return formula

# UPDATE
@router.put("/{formula_id}", response_model=FormulaResponse)
def update_formula(formula_id: int, payload: FormulaUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(formula, key, value)
    db.commit()
    db.refresh(formula)
    return formula

# DELETE
@router.delete("/{formula_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_formula(formula_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    db.delete(formula)
    db.commit()
    return {"message": "Formula deleted successfully"}
