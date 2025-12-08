# app/routes/job_posting_routes.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.job_posting_m import JobPosting, ApprovalStatus
from app.models.candidate_m import Candidate
from app.models.user_m import User
from app.models.role_m import Role
from app.models.notification_m import Notification

from app.schemas.job_posting_schema import (
    AcceptedCandidateResponse,
    JobPostingCreate,
    JobPostingUpdate,
    JobPostingResponse,
)

from app.utils.email_utils import send_template_email
from app.config import settings

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/job-postings", tags=["Job Postings"])
MENU_ID = 61


# ------------------------------------------------------
# CREATE JOB POSTING
# ------------------------------------------------------
@router.post("/", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    data: JobPostingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(MENU_ID)),
):
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can create job postings.",
        )

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

    job = JobPosting(
        **data.model_dump(),
        created_by_id=current_user.id,
        created_by_name=current_user.first_name,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    admin_users = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(Role.role.ilike("admin"), User.inactive == False)
        .all()
    )

    admin_emails = []
    for admin in admin_users:
        db.add(
            Notification(
                candidate_id=None,
                message=f"New Job Posted: job id {job.id} — location {job.location}",
            )
        )
        if admin.email:
            admin_emails.append(admin.email)

    db.commit()

    if admin_emails:
        subject = f"New Job Posted — Job ID {job.id}"
        html_body = f"""
        <p>Hi Admin,</p>
        <p>A new job has been posted:</p>
        <ul>
            <li>Job ID: {job.id}</li>
            <li>Role ID: {job.job_description_id}</li>
            <li>Location: {job.location}</li>
        </ul>
        <p>Regards,<br/>{settings.COMPANY_NAME}</p>
        """
        background_tasks.add_task(
    send_template_email,
    admin_emails,
    subject,
    "new_job.html",
    {
        "job_id": job.id,
        "location": job.location,
        "role_id": job.job_description_id
    }
)


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
# UPDATE
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

    posting.modified_by = current_user.first_name
    posting.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(posting)

    return JobPostingResponse.model_validate(posting)


# ------------------------------------------------------
# DELETE
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
# FILTER
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
# ------------------------------------------------------
@router.get("/admin/dashboard")
def admin_dashboard(
    job_posting_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    if job_posting_id:
        total_jobs = db.query(JobPosting).filter(JobPosting.id == job_posting_id).count()
    else:
        total_jobs = db.query(JobPosting).count()

    return {
        "total_jobs": total_jobs,
        "total_candidates": db.query(Candidate).count(),
        "accepted_jobs": db.query(JobPosting).filter(JobPosting.approval_status == ApprovalStatus.accepted).count(),
        "pending_jobs": db.query(JobPosting).filter(JobPosting.approval_status == ApprovalStatus.pending).count(),
    }


# ------------------------------------------------------
# ACCEPTED CANDIDATES
# ------------------------------------------------------
@router.get("/accepted-candidates", response_model=List[AcceptedCandidateResponse])
def get_accepted_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID)),
    job_posting_id: Optional[int] = None
):
    query = (
        db.query(Candidate)
        .join(JobPosting, Candidate.job_posting_id == JobPosting.id)
        .filter(JobPosting.approval_status == ApprovalStatus.accepted)
    )

    if job_posting_id:
        query = query.filter(Candidate.job_posting_id == job_posting_id)

    return [AcceptedCandidateResponse.model_validate(c) for c in query.all()]
