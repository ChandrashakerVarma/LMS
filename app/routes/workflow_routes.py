from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workflow_m import Workflow, ApprovalStatus
from app.schema.workflow_schema import WorkflowCreate, WorkflowUpdate, WorkflowOut

router = APIRouter(prefix="/job_posting_workflows", tags=["Job Posting Workflow"])

# ✅ CREATE
@router.post("/", response_model=WorkflowOut)
def create_workflow(flow: WorkflowCreate, db: Session = Depends(get_db)):
    new_flow = Workflow(**flow.dict())
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)
    return new_flow


# ✅ READ ALL
@router.get("/", response_model=list[WorkflowOut])
def get_all_workflows(db: Session = Depends(get_db)):
    workflows = db.query(Workflow).all()
    return workflows


# ✅ READ ONE
@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow_by_id(workflow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return flow


# ✅ UPDATE (general update)
@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: int, updated_data: WorkflowUpdate, db: Session = Depends(get_db)):
    flow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(flow, key, value)

    db.commit()
    db.refresh(flow)
    return flow


# ✅ DELETE
@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db.delete(flow)
    db.commit()
    return {"message": f"Workflow with id {workflow_id} deleted successfully"}


# ✅ APPROVE
@router.put("/{workflow_id}/approve", response_model=WorkflowOut)
def approve_workflow(workflow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    flow.approval_status = ApprovalStatus.Approved
    db.commit()
    db.refresh(flow)
    return flow


# ✅ REJECT
@router.put("/{workflow_id}/reject", response_model=WorkflowOut)
def reject_workflow(workflow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    flow.approval_status = ApprovalStatus.Rejected
    db.commit()
    db.refresh(flow)
    return flow
