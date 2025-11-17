from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.job_posting_m import JobPosting
from app.models.workflow_m import Workflow, ApprovalStatus
from app.models.candidate_m import Candidate
from app.models.notification_m import Notification
from app.models.user_m import User
from app.schema.job_posting_schema import JobPostingCreate, JobPostingUpdate, JobPostingOut
from app.dependencies import require_admin

router = APIRouter(prefix="/job_postings", tags=["Job Postings"])

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
@router.post("/", response_model=JobPostingOut)
def create_job_posting(
    data: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    job = JobPosting(
        **data.dict(),
        created_by_id=current_user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Create workflow
    workflow = Workflow(
        posting_id=job.id,
        approval_status=ApprovalStatus.pending
    )
    db.add(workflow)
    db.commit()

    # Notify candidates
    candidates = db.query(Candidate).all()
    for c in candidates:
        note = Notification(
            candidate_id=c.id,
            message=f"New Job Posted: Role ID {job.job_role_id} at {job.location}"
        )
        db.add(note)
    db.commit()

    return job


# ---------------- FILTER JOB POSTINGS ----------------
@router.get("/filters", response_model=List[JobPostingOut])
def filter_jobs(
    location: Optional[str] = None,
    role_id: Optional[int] = None,
    min_salary: Optional[int] = None,
    employment_type: Optional[str] = None,
    db: Session = Depends(get_db)
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
    return query.all()


# ---------------- ADMIN DASHBOARD ----------------
@router.get("/admin/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
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
def get_all_job_postings(db: Session = Depends(get_db)):
    return db.query(JobPosting).all()


# ---------------- GET JOB POSTING BY ID ----------------
@router.get("/{job_posting_id}", response_model=JobPostingOut)
def get_job_posting(job_posting_id: int, db: Session = Depends(get_db)):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return posting


# ---------------- UPDATE JOB POSTING ----------------
@router.put("/{job_posting_id}", response_model=JobPostingOut)
def update_job_posting(
    job_posting_id: int,
    updated: JobPostingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    if posting.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this posting")

    for key, value in updated.dict(exclude_unset=True).items():
        setattr(posting, key, value)
    db.commit()
    db.refresh(posting)
    return posting


# ---------------- DELETE JOB POSTING ----------------
@router.delete("/{job_posting_id}")
def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    if posting.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this posting")

    db.delete(posting)
    db.commit()
    return {"detail": "Job posting deleted successfully"}


# ---------------- GET ALL ACCEPTED CANDIDATES (ADMIN) ----------------
@router.get("/accepted-candidates", response_model=List[AcceptedCandidateOut])
def get_accepted_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    job_posting_id: Optional[int] = None  # optional filter
):
    """
    Admin endpoint to list all candidates whose job posting workflow is accepted.
    Can optionally filter by a specific job_posting_id.
    """
    query = db.query(Candidate).join(Workflow, Candidate.workflow_id == Workflow.id).join(JobPosting)

    query = query.filter(Workflow.approval_status == ApprovalStatus.accepted)
    if job_posting_id:
        query = query.filter(Candidate.job_posting_id == job_posting_id)

    accepted_candidates = query.all()

    if not accepted_candidates:
        return []

    # serialize candidate with related job posting info
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
