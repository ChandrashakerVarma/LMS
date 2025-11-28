from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.job_posting_m import JobPosting
from app.models.workflow_m import Workflow, ApprovalStatus
from app.models.candidate_m import Candidate
from app.models.notification_m import Notification
from app.models.user_m import User
from app.Schema.job_posting_schema import JobPostingCreate, JobPostingUpdate, JobPostingOut

# Import new permission dependencies
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/job-postings", tags=["Job Postings"])


# -------------------- Pydantic Schema for Accepted Candidates --------------------
class AcceptedCandidateOut(BaseModel):
    candidate_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    job_posting_id: int
    job_role_id: int
    location: str
    status: str

    class Config:
        orm_mode = True


# ---------------- CREATE JOB POSTING ----------------
@router.post("/", response_model=JobPostingOut, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    data: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(61))
):
    existing_job = db.query(JobPosting).filter(
        JobPosting.job_role_id == data.job_role_id,
        JobPosting.location == data.location,
        JobPosting.employment_type == data.employment_type
    ).first()

    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job posting with the same role, location, and employment type already exists."
        )

    job = JobPosting(
        **data.dict(),
        created_by=current_user.first_name
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    workflow = Workflow(
        posting_id=job.id,
        approval_status=ApprovalStatus.pending
    )
    db.add(workflow)
    db.commit()

    candidates = db.query(Candidate).all()
    for c in candidates:
        note = Notification(
            candidate_id=c.id,
            message=f"New Job Posted: Role ID {job.job_role_id} at {job.location}"
        )
        db.add(note)

    db.commit()

    return JobPostingOut.from_orm(job)


# ---------------- FILTER JOB POSTINGS ----------------
@router.get("/filters", response_model=List[JobPostingOut])
def filter_jobs(
    location: Optional[str] = None,
    role_id: Optional[int] = None,
    min_salary: Optional[int] = None,
    employment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(61))
):
    query = db.query(JobPosting)

    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))
    if role_id:
        query = query.filter(JobPosting.job_role_id == role_id)
    if min_salary:
        query = query.filter(JobPosting.salary >= min_salary)
    if employment_type:
        query = query.filter(JobPosting.employment_type == employment_type)

    return [JobPostingOut.from_orm(p) for p in query.all()]


# ---------------- ADMIN DASHBOARD ----------------
@router.get("/admin/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(61))
):
    total_jobs = db.query(JobPosting).count()
    total_candidates = db.query(Candidate).count()
    accepted = db.query(Workflow).filter(Workflow.approval_status == ApprovalStatus.accepted).count()
    pending = db.query(Workflow).filter(Workflow.approval_status == ApprovalStatus.pending).count()

    return {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "accepted_candidates": accepted,
        "pending_approvals": pending
    }


# ---------------- GET ALL JOB POSTINGS ----------------
@router.get("/", response_model=List[JobPostingOut])
def get_all_job_postings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(61))
):
    postings = db.query(JobPosting).all()
    return [JobPostingOut.from_orm(p) for p in postings]


# ---------------- GET JOB POSTING BY ID ----------------
@router.get("/{job_posting_id}", response_model=JobPostingOut)
def get_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(61))
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    return JobPostingOut.from_orm(posting)


# ---------------- UPDATE JOB POSTING ----------------
@router.put("/{job_posting_id}", response_model=JobPostingOut)
def update_job_posting(
    job_posting_id: int,
    updated: JobPostingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(61))
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    for key, value in updated.dict(exclude_unset=True).items():
        setattr(posting, key, value)

    posting.modified_by = current_user.first_name
    posting.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(posting)
    return JobPostingOut.from_orm(posting)


# ---------------- DELETE JOB POSTING ----------------
@router.delete("/{job_posting_id}")
def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete_permission(61))
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    db.query(Workflow).filter(Workflow.posting_id == job_posting_id).delete()
    db.commit()

    db.delete(posting)
    db.commit()

    return {"detail": "Job posting deleted successfully"}


# ---------------- GET ALL ACCEPTED CANDIDATES ----------------
@router.get("/accepted-candidates", response_model=List[AcceptedCandidateOut])
def get_accepted_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(61)),
    job_posting_id: Optional[int] = None
):
    query = db.query(Candidate).join(Workflow, Candidate.workflow_id == Workflow.id).join(JobPosting)
    query = query.filter(Workflow.approval_status == ApprovalStatus.accepted)

    if job_posting_id:
        query = query.filter(Candidate.job_posting_id == job_posting_id)

    accepted_candidates = query.all()

    result = []
    for c in accepted_candidates:
        result.append({
            "candidate_id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone_number": c.phone_number,
            "job_posting_id": c.job_posting.id,
            "job_role_id": c.job_posting.job_role_id,
            "location": c.job_posting.location,
            "status": c.status
        })

    return result
