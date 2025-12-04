# app/routes/candidates_routes.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.candidate_m import Candidate
from app.models.notification_m import Notification
from app.models.user_m import User
from app.models.role_m import Role

from app.schemas.candidate_schema import (
    CandidateCreate,
    CandidateResponse,
    CandidateUpdate
)

from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

from app.utils.email_utils import send_email
from app.config import settings

router = APIRouter(prefix="/candidates", tags=["Candidates"])

CANDIDATES_MENU_ID = 64
# -----------------------------------------------------------
# PUBLIC APPLY (NO AUTH)
# -----------------------------------------------------------
@router.post("/apply", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    payload: CandidateCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Public endpoint — candidate applies without auth."""
    
    db_candidate = Candidate(**payload.model_dump())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    # Notify admins
    admin_users = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(Role.role.ilike("admin"), User.inactive == False)
        .all()
    )

    admin_emails = []

    for admin in admin_users:
        message = (
            f"New candidate applied — {db_candidate.first_name} {db_candidate.last_name}, "
            f"Job ID: {db_candidate.job_posting_id}"
        )

        db.add(Notification(candidate_id=db_candidate.id, message=message))

        if admin.email:
            admin_emails.append(admin.email)

    db.commit()

    # Email admins (optional)
    if admin_emails:
        company = getattr(settings, "COMPANY_NAME", "Your Company")
        subject = f"New Candidate Application — {db_candidate.first_name}"
        html_body = f"""
        <p>A new candidate has applied for a job.</p>
        <ul>
            <li>Name: {db_candidate.first_name} {db_candidate.last_name}</li>
            <li>Email: {db_candidate.email}</li>
            <li>Phone: {db_candidate.phone_number}</li>
            <li>Job Posting ID: {db_candidate.job_posting_id}</li>
        </ul>
        <p>Regards,<br>{company}</p>
        """
        background_tasks.add_task(send_email, admin_emails, subject, html_body)

    return CandidateResponse.from_orm(db_candidate)


# -----------------------------------------------------------
# GET ALL CANDIDATES
# -----------------------------------------------------------
@router.get(
    "/",
    response_model=List[CandidateResponse],
    dependencies=[Depends(require_view_permission(CANDIDATES_MENU_ID))]
)
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    return [CandidateResponse.from_orm(c) for c in candidates]


# -----------------------------------------------------------
# GET ONE CANDIDATE
# -----------------------------------------------------------
@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
    dependencies=[Depends(require_view_permission(CANDIDATES_MENU_ID))]
)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return CandidateResponse.from_orm(candidate)


# -----------------------------------------------------------
# UPDATE CANDIDATE
# -----------------------------------------------------------
@router.put(
    "/{candidate_id}",
    response_model=CandidateResponse,
    dependencies=[Depends(require_edit_permission(CANDIDATES_MENU_ID))]
)
def update_candidate(
    candidate_id: int,
    updated_data: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    update_values = updated_data.model_dump(exclude_unset=True)
    update_values["modified_by"] = current_user.username

    for key, value in update_values.items():
        setattr(candidate, key, value)

    candidate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(candidate)

    return CandidateResponse.from_orm(candidate)


# -----------------------------------------------------------
# DELETE CANDIDATE
# -----------------------------------------------------------
@router.delete(
    "/{candidate_id}",
    dependencies=[Depends(require_delete_permission(CANDIDATES_MENU_ID))]
)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()

    return {"message": f"Candidate deleted by {current_user.username}"}


# -----------------------------------------------------------
# UPDATE STATUS (ACCEPT / REJECT)
# -----------------------------------------------------------
@router.put(
    "/{candidate_id}/status",
    dependencies=[Depends(require_edit_permission(CANDIDATES_MENU_ID))]
)
async def update_candidate_status(
    candidate_id: int,
    status: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = status
    candidate.modified_by = current_user.username
    candidate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(candidate)

    # Prepare notification + email
    job = candidate.job_posting
    job_title = job.job_description.title if job and job.job_description else "the job role"
    company = getattr(settings, "COMPANY_NAME", "Your Company")

    if status.lower() == "accepted":
        subject = f"Congratulations — {job_title}"
        html_body = f"""
        <h2>Congratulations {candidate.first_name}!</h2>
        <p>You have been accepted for <strong>{job_title}</strong>.</p>
        """
    elif status.lower() == "rejected":
        subject = f"Application Update — {job_title}"
        html_body = f"""
        <h2>Hello {candidate.first_name},</h2>
        <p>Your application for <strong>{job_title}</strong> was not selected.</p>
        """
    else:
        subject = f"Application Status Update — {job_title}"
        html_body = f"Your status changed to: {status}"

    # Save notification
    db.add(Notification(candidate_id=candidate.id, message=html_body))
    db.commit()

    # Send email
    if candidate.email:
        background_tasks.add_task(send_email, [candidate.email], subject, html_body)

    return {
        "candidate_id": candidate.id,
        "status": candidate.status,
        "detail": "Status updated, notification saved, email sent"
    }
