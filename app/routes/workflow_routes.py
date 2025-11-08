from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.workflow_m import Workflow
from app.schema.workflow_schema import WorkflowCreate, WorkflowUpdate, WorkflowOut

router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"]
)

# ✅ Create workflow
@router.post("/", response_model=WorkflowOut)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    new_workflow = Workflow(**workflow.dict())
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)
    return new_workflow

# ✅ Get all workflows
@router.get("/", response_model=List[WorkflowOut])
def get_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).all()

# ✅ Get workflow by ID
@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf

# ✅ Update workflow
@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: int, workflow: WorkflowUpdate, db: Session = Depends(get_db)):
    db_wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    for key, value in workflow.dict().items():
        setattr(db_wf, key, value)

    db.commit()
    db.refresh(db_wf)
    return db_wf

# ✅ Delete workflow
@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    db_wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(db_wf)
    db.commit()
    return {"detail": "Workflow deleted successfully"}
