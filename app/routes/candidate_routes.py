# app/routes/candidates_routes.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
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
        .filter(Role.name.ilike("admin"), User.inactive == False)
        .all()
    )

    admin_emails = []

    for admin in admin_users:
        msg = (
            f"New candidate applied — {db_candidate.first_name} {db_candidate.last_name}, "
            f"Job ID: {db_candidate.job_posting_id}"
        )

        db.add(Notification(candidate_id=db_candidate.id, message=msg))

        if admin.email:
            admin_emails.append(admin.email)

    db.commit()

    # Email admins
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
    return db.query(Candidate).all()


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
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    update_values = payload.model_dump(exclude_unset=True)
    update_values["modified_by"] = current_user.first_name

    for key, value in update_values.items():
        setattr(candidate, key, value)

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

    return {"message": f"Candidate deleted by {current_user.first_name}"}
