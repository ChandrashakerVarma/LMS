from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workflow_m import Workflow, ApprovalStatus
from app.schema.workflow_schema import WorkflowCreate, WorkflowOut

router = APIRouter(prefix="/job_posting_workflows", tags=["Job Posting Workflow"])


@router.post("/", response_model=WorkflowOut)
def create_workflow(flow: WorkflowCreate, db: Session = Depends(get_db)):
    new_flow = Workflow(**flow.dict())
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)
    return new_flow


@router.put("/{workflow_id}/approve", response_model=WorkflowOut)
def approve_workflow(workflow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    flow.approval_status = ApprovalStatus.Approved
    db.commit()
    db.refresh(flow)
    return flow


@router.put("/{workflow_id}/reject", response_model=WorkflowOut)
def reject_workflow(workflow_id: int, db: Session = Depends(get_db)):
    flow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    flow.approval_status = ApprovalStatus.Rejected
    db.commit()
    db.refresh(flow)
    return flow
