# app/routes/job_posting_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.job_posting_m import JobPosting, ApprovalStatus
from app.models.candidate_m import Candidate
from app.models.user_m import User

from app.schema.job_posting_schema import JobPostingCreate, JobPostingUpdate, JobPostingResponse

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/job-postings", tags=["Job Postings"])
MENU_ID = 61

# ------------------------------------------------------
# CREATE JOB POSTING  (ADMIN ONLY)
# ------------------------------------------------------
@router.post("/", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    data: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(MENU_ID)),
):
    # -------- ADMIN ONLY CHECK --------
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins are allowed to create job postings."
        )

    # Duplicate job check
    existing_job = (
        db.query(JobPosting)
        .filter(
            JobPosting.job_description_id == data.job_description_id,
            JobPosting.location == data.location,
            JobPosting.employment_type == data.employment_type,
        )
        .first()
    )
    if existing_job:
        raise HTTPException(
            status_code=400,
            detail="Job posting with same role, location, and employment type already exists.",
        )

    # Create job posting
    job = JobPosting(
        **data.model_dump(),
        created_by=current_user.first_name
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobPostingResponse.model_validate(job)


# ------------------------------------------------------
# GET ALL POSTINGS
# ------------------------------------------------------
@router.get("/", response_model=List[JobPostingResponse])
def get_all_job_postings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    postings = db.query(JobPosting).all()
    return [JobPostingResponse.model_validate(p) for p in postings]


# ------------------------------------------------------
# UPDATE POSTING
# ------------------------------------------------------
@router.put("/{job_posting_id}", response_model=JobPostingResponse)
def update_job_posting(
    job_posting_id: int,
    updated: JobPostingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(posting, key, value)

    posting.modified_by = current_user.first_name if current_user else None
    posting.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(posting)

    return JobPostingResponse.model_validate(posting)


# ------------------------------------------------------
# DELETE POSTING
# ------------------------------------------------------
@router.delete("/{job_posting_id}")
def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete_permission(MENU_ID))
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    db.delete(posting)
    db.commit()

    return {"detail": "Job posting deleted successfully"}


# ------------------------------------------------------
# FILTER POSTINGS
# ------------------------------------------------------
@router.get("/filters", response_model=List[JobPostingResponse])
def filter_jobs(
    location: Optional[str] = None,
    role_id: Optional[int] = None,
    min_salary: Optional[int] = None,
    employment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    query = db.query(JobPosting)

    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))
    if role_id:
        query = query.filter(JobPosting.job_description_id == role_id)
    if min_salary:
        query = query.filter(JobPosting.salary >= min_salary)
    if employment_type:
        query = query.filter(JobPosting.employment_type == employment_type)

    postings = query.all()
    return [JobPostingResponse.model_validate(p) for p in postings]

# ------------------------------------------------------
# ADMIN DASHBOARD
@router.get("/dashboard")
def admin_dashboard(
    job_posting_id: Optional[int] = Query(default=None, description="Optional Job Posting ID to filter stats"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    if job_posting_id:
        jobs = db.query(JobPosting).filter(JobPosting.id == job_posting_id).all()
    else:
        jobs = db.query(JobPosting).all()

    dashboard_data = []
    for job in jobs:
        candidates = db.query(Candidate).filter(Candidate.job_posting_id == job.id)
        dashboard_data.append({
            "job_id": job.id,
            "role": job.job_description.title if job.job_description else "",
            "location": job.location,
            "approval_status": job.approval_status,
            "total_candidates": candidates.count(),
            "pending_candidates": candidates.filter(Candidate.status == "Pending").count(),
            "accepted_candidates": candidates.filter(Candidate.status == "Accepted").count(),
            "rejected_candidates": candidates.filter(Candidate.status == "Rejected").count()
        })

    return dashboard_data



# ------------------------------------------------------
# GET SINGLE POSTING
# ------------------------------------------------------
@router.get("/{job_posting_id}", response_model=JobPostingResponse)
def get_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    return JobPostingResponse.model_validate(posting)

