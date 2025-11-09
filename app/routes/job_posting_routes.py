from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.job_posting_m import JobPosting
from app.schema.job_posting_schema import JobPostingCreate, JobPostingOut
from app.models.workflow_m import Workflow, ApprovalStatus
from app.models.candidate_m import Candidate
from app.schema.candidate_schema import CandidateOut

router = APIRouter(prefix="/job_postings", tags=["Job Postings"])

# ✅ Create a new job posting
@router.post("/", response_model=JobPostingOut)
def create_job_posting(job_posting: JobPostingCreate, db: Session = Depends(get_db)):
    new_posting = JobPosting(**job_posting.dict())
    db.add(new_posting)
    db.commit()
    db.refresh(new_posting)
    return new_posting


# ✅ Get all job postings
@router.get("/", response_model=List[JobPostingOut])
def get_all_job_postings(db: Session = Depends(get_db)):
    return db.query(JobPosting).all()


# ✅ Get a single job posting by ID
@router.get("/{job_id}", response_model=JobPostingOut)
def get_job_posting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


# ✅ Update a job posting
@router.put("/{job_id}", response_model=JobPostingOut)
def update_job_posting(job_id: int, updated_data: JobPostingCreate, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    for key, value in updated_data.dict().items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


# ✅ Delete a job posting
@router.delete("/{job_id}")
def delete_job_posting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    db.delete(job)
    db.commit()
    return {"message": "Job posting deleted successfully"}

@router.get("/{job_id}/candidates/accepted", response_model=List[CandidateOut])
def get_accepted_candidates(job_id: int, db: Session = Depends(get_db)):
    """
    Get all accepted candidates for a given job posting
    """
    # Check if the job exists
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Get workflows with approved/accepted status
    accepted_workflows = db.query(Workflow).filter(
        Workflow.posting_id == job_id,
        Workflow.approval_status == ApprovalStatus.accepted
    ).all()

    # Collect all candidates from accepted workflows
    accepted_candidates = []
    for workflow in accepted_workflows:
        candidates = db.query(Candidate).filter(Candidate.workflow_id == workflow.id).all()
        accepted_candidates.extend(candidates)

    return accepted_candidates