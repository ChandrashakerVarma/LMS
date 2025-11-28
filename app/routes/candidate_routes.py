# app/routes/candidates_routes.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.candidate_m import Candidate
<<<<<<< HEAD
from app.Schema.candidate_schema import CandidateCreate, CandidateOut, CandidateUpdate
=======
from app.models.notification_m import Notification
from app.models.user_m import User
from app.models.role_m import Role
from app.schema.candidate_schema import CandidateCreate, CandidateResponse, CandidateUpdate
from app.utils.email_utils import send_email
>>>>>>> origin/main

from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

from app.config import settings

router = APIRouter(prefix="/candidates", tags=["Candidates"])

# Menu ID for candidate permissions
CANDIDATES_MENU_ID = 64


# -------------------- Public Apply (no auth) --------------------
@router.post("/apply", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def apply_for_job(payload: CandidateCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Public endpoint for candidates to apply.
    - Creates Candidate record
    - Creates Notification(s) for admin users
    - Optionally sends a short admin email (background)
    """
    # Create candidate record
    data = payload.model_dump()
    # If you want to store IP / source, add fields to schema and model
    db_candidate = Candidate(**data)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    # Create notifications for admins
    admin_users = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(Role.role.ilike("admin"), User.inactive == False)
        .all()
    )

    admin_emails: List[str] = []
    for admin in admin_users:
        # Create notification row
        note_msg = (
            f"New application: {db_candidate.first_name} {db_candidate.last_name} applied for job id {db_candidate.job_posting_id}"
        )
        note = Notification(candidate_id=db_candidate.id, message=note_msg)
        db.add(note)

        # collect admin email for optional notification email
        if getattr(admin, "email", None):
            admin_emails.append(admin.email)

    db.commit()

    # Optional: send short admin notification email in background
    if admin_emails:
        company = getattr(settings, "COMPANY_NAME", "Your Company")
        subject = f"New Candidate Application — {db_candidate.first_name} {db_candidate.last_name}"
        html_body = f"""
            <p>Hi Admin,</p>
            <p>A new candidate has applied.</p>
            <ul>
              <li><strong>Name:</strong> {db_candidate.first_name} {db_candidate.last_name}</li>
              <li><strong>Email:</strong> {db_candidate.email}</li>
              <li><strong>Phone:</strong> {db_candidate.phone_number}</li>
              <li><strong>Applied for job id:</strong> {db_candidate.job_posting_id}</li>
            </ul>
            <p>Open the admin panel to review the candidate.</p>
            <p>Regards,<br/>{company}</p>
        """
        background_tasks.add_task(send_email, admin_emails, subject, html_body)

    return CandidateResponse.from_orm(db_candidate)




# -------------------- Get All Candidates --------------------
@router.get(
    "/",
    response_model=List[CandidateResponse],
    dependencies=[Depends(require_view_permission(CANDIDATES_MENU_ID))]
)
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    return [CandidateResponse.from_orm(c) for c in candidates]


# -------------------- Get Candidate by ID --------------------
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


# -------------------- Update Candidate --------------------
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
    update_values["modified_by"] = current_user.username if current_user else None

    for key, value in update_values.items():
        setattr(candidate, key, value)

    candidate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(candidate)
    return CandidateResponse.from_orm(candidate)


# -------------------- Delete Candidate --------------------
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


# -------------------- Update Candidate Status (accept/reject) --------------------
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
    """
    Admin endpoint to update candidate status.
    - Saves notification
    - Sends acceptance / rejection email in background
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Update status & audit
    candidate.status = status
    candidate.modified_by = current_user.username if current_user else None
    candidate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(candidate)

    # Compose email + notification
    job_title = candidate.job_posting.job_description.title if candidate.job_posting and getattr(candidate.job_posting, "job_description", None) else "the role"
    company_name = getattr(settings, "COMPANY_NAME", "Your Company")
    company_logo = getattr(settings, "COMPANY_LOGO_URL", None)
    location = getattr(candidate.job_posting, "location", "Not specified")
    interview_datetime = getattr(candidate, "interview_datetime", None)  # optional

    if status.lower() == "accepted":
        subject = f"Congratulations — {job_title} at {company_name}"
        html_body = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; max-width:600px;">
              <div style="text-align:center;">
                {'<img src="'+company_logo+'" alt="Company Logo" style="max-height:80px;"/>' if company_logo else f'<h2>{company_name}</h2>'}
              </div>
              <h3>Congratulations {candidate.first_name} {candidate.last_name}!</h3>
              <p>Your application for <strong>{job_title}</strong> has been <strong>accepted</strong>.</p>
              <p><strong>Location:</strong> {location}</p>
              {f"<p><strong>Date & Time:</strong> {interview_datetime}</p>" if interview_datetime else ""}
              <p>We will contact you shortly with further details.</p>
              <br/>
              <p>Best regards,<br/>{company_name}</p>
            </div>
          </body>
        </html>
        """
        text_body = f"Congratulations {candidate.first_name}! Your application for {job_title} has been accepted. Location: {location}."
    elif status.lower() == "rejected":
        subject = f"Application Update — {job_title}"
        html_body = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; max-width:600px;">
              <div style="text-align:center;">
                {'<img src="'+company_logo+'" alt="Company Logo" style="max-height:80px;"/>' if company_logo else f'<h2>{company_name}</h2>'}
              </div>
              <h3>Hi {candidate.first_name} {candidate.last_name},</h3>
              <p>Thank you for applying for <strong>{job_title}</strong>. We appreciate your interest in {company_name}.</p>
              <p>After careful review, we regret to inform you that your application was not selected for this role.</p>
              <p>We encourage you to apply for other opportunities in the future.</p>
              <br/>
              <p>Kind regards,<br/>{company_name}</p>
            </div>
          </body>
        </html>
        """
        text_body = f"Hi {candidate.first_name}, thank you for applying for {job_title}. We regret to inform you your application was not selected."
    else:
        subject = f"Application Status Update — {job_title}"
        html_body = f"<p>Your application status has been updated to: {status}</p>"
        text_body = f"Your application status has been updated to: {status}"

    # Save notification (for record)
    notification = Notification(candidate_id=candidate.id, message=html_body)
    db.add(notification)
    db.commit()

    # Send email to candidate
    if candidate.email:
        background_tasks.add_task(send_email, [candidate.email], subject, html_body, text_body)

    return {
        "candidate_id": candidate.id,
        "status": candidate.status,
        "notification": "Saved",
        "detail": "Status updated, notification saved, and email scheduled."
    }
