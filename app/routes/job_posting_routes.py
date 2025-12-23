from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.job_posting_m import JobPosting, JobType
from app.models.candidate_m import Candidate
from app.models.user_m import User

from app.schema.job_posting_schema import (
    JobPostingCreate,
    JobPostingUpdate,
    JobPostingResponse
)

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(
    prefix="/job-postings",
    tags=["Job Postings"]
)

MENU_ID = 61

# ------------------------------------------------------
# CREATE JOB POSTING
# ------------------------------------------------------
@router.post(
    "/",
    response_model=JobPostingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job_posting(
    data: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(MENU_ID)),
):
    # Role validation
    if current_user.role.name not in ["super_admin", "org_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only Admin or Super Admin can create job postings"
        )

    # Org-level restriction
    if current_user.role.name != "super_admin":
        if data.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403,
                detail="You can create jobs only for your organization"
            )

    # Duplicate check
    existing = db.query(JobPosting).filter(
        JobPosting.job_description_id == data.job_description_id,
        JobPosting.location == data.location,
        JobPosting.employment_type == data.employment_type,
        JobPosting.organization_id == data.organization_id,
        JobPosting.branch_id == data.branch_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Job posting already exists for this role, location and branch"
        )

    job = JobPosting(
        **data.model_dump(),
        created_by=current_user.first_name
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return JobPostingResponse.model_validate(job)


# ------------------------------------------------------
# GET ALL JOB POSTINGS
# ------------------------------------------------------
@router.get("/", response_model=List[JobPostingResponse])
def get_all_job_postings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    query = db.query(JobPosting)

    if current_user.role.name != "super_admin":
        query = query.filter(
            JobPosting.organization_id == current_user.organization_id
        )

    postings = query.order_by(JobPosting.created_at.desc()).all()
    return [JobPostingResponse.model_validate(p) for p in postings]



# ------------------------------------------------------
# UPDATE JOB POSTING
# ------------------------------------------------------
@router.put("/{job_posting_id}", response_model=JobPostingResponse)
def update_job_posting(
    job_posting_id: int,
    updated: JobPostingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID)),
):
    posting = db.query(JobPosting).filter(
        JobPosting.id == job_posting_id
    ).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    if current_user.role.name != "super_admin":
        if posting.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")

    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(posting, key, value)

    posting.modified_by = current_user.first_name
    posting.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(posting)

    return JobPostingResponse.model_validate(posting)


# ------------------------------------------------------
# DELETE JOB POSTING
# ------------------------------------------------------
@router.delete("/{job_posting_id}", status_code=status.HTTP_200_OK)
def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete_permission(MENU_ID)),
):
    posting = db.query(JobPosting).filter(
        JobPosting.id == job_posting_id
    ).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    if current_user.role.name != "super_admin":
        if posting.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")

    db.delete(posting)
    db.commit()

    return {"detail": "Job posting deleted successfully"}


# ------------------------------------------------------
# FILTER JOB POSTINGS
# ------------------------------------------------------
@router.get("/filters", response_model=List[JobPostingResponse])
def filter_job_postings(
    location: Optional[str] = None,
    job_type: Optional[JobType] = None,
    role_id: Optional[int] = None,
    min_salary: Optional[int] = None,
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    query = db.query(JobPosting)

    if current_user.role.name != "super_admin":
        query = query.filter(
            JobPosting.organization_id == current_user.organization_id
        )

    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))

    if job_type:
        query = query.filter(JobPosting.job_type == job_type)

    if role_id:
        query = query.filter(JobPosting.job_description_id == role_id)

    if branch_id:
        query = query.filter(JobPosting.branch_id == branch_id)

    if min_salary:
        query = query.filter(JobPosting.salary >= min_salary)

    postings = query.all()
    return [JobPostingResponse.model_validate(p) for p in postings]


# ------------------------------------------------------
# ADMIN DASHBOARD
# ------------------------------------------------------
@router.get("/dashboard")
def job_dashboard(
    job_posting_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID)),
):
    query = db.query(JobPosting)

    # Only show jobs for the user's organization unless super_admin
    if current_user.role.name != "super_admin":
        query = query.filter(JobPosting.organization_id == current_user.organization_id)

    if job_posting_id:
        query = query.filter(JobPosting.id == job_posting_id)

    jobs = query.all()
    dashboard = []

    for job in jobs:
        candidates_query = db.query(Candidate).filter(Candidate.job_posting_id == job.id)

        dashboard.append({
            "job_id": job.id,
            "job_type": job.job_type,
            "role": job.job_description.title if job.job_description else "",
            "location": job.location,
            "approval_status": job.approval_status,
            "total_candidates": candidates_query.count(),
            "pending": candidates_query.filter(Candidate.status == "Pending").count(),
            "accepted": candidates_query.filter(Candidate.status == "Accepted").count(),
            "rejected": candidates_query.filter(Candidate.status == "Rejected").count(),
        })

    return dashboard


# ------------------------------------------------------
# GET SINGLE JOB POSTING
# ------------------------------------------------------
@router.get("/{job_posting_id}", response_model=JobPostingResponse)
def get_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    posting = db.query(JobPosting).filter(
        JobPosting.id == job_posting_id
    ).first()

    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    if current_user.role.name != "super_admin":
        if posting.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return JobPostingResponse.model_validate(posting)
