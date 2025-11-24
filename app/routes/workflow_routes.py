from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.workflow_m import Workflow
from app.schema.workflow_schema import WorkflowCreate, WorkflowUpdate, WorkflowResponse

# ✅ Import specific permission checks
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])

MENU_ID = 63   # Workflow menu ID


# ---------------- CREATE WORKFLOW ----------------
@router.post("/", response_model=WorkflowResponse)
def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_create_permission(MENU_ID))
):
    new_wf = Workflow(**workflow.dict())
    db.add(new_wf)
    db.commit()
    db.refresh(new_wf)
    return WorkflowResponse.from_orm(new_wf)


# ---------------- GET ALL WORKFLOWS ----------------
@router.get("/", response_model=List[WorkflowResponse])
def get_workflows(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_view_permission(MENU_ID))
):
    workflows = db.query(Workflow).all()
    return [WorkflowResponse.from_orm(wf) for wf in workflows]


# ---------------- GET WORKFLOW BY ID ----------------
@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_view_permission(MENU_ID))
):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.from_orm(wf)


# ---------------- UPDATE WORKFLOW ----------------
@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: int,
    workflow: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_edit_permission(MENU_ID))
):
    db_wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    for key, value in workflow.dict(exclude_unset=True).items():
        setattr(db_wf, key, value)

    db.commit()
    db.refresh(db_wf)
    return WorkflowResponse.from_orm(db_wf)


# ---------------- DELETE WORKFLOW ----------------
@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_delete_permission(MENU_ID))
):
    db_wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db.delete(db_wf)
    db.commit()
    return {"detail": "Workflow deleted successfully"}
