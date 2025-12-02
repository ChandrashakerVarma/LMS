from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.candidate_m import Candidate
from app.models.notification_m import Notification
from app.models.user_m import User
from app.models.job_posting_m import JobPosting
from app.schema.candidate_schema import CandidateCreate, CandidateResponse, CandidateUpdate
from app.s3_helper import upload_file_to_s3
from app.utils.email_templates_utils import render_email
from app.utils.email_ses import send_email_ses

router = APIRouter(prefix="/candidates", tags=["Candidates"])


# -------------------------------------
# Apply for a job
# -------------------------------------

@router.post("/", response_model=CandidateResponse)
def apply_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):

    candidate = Candidate(**payload.dict())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Fetch job
    job = db.query(JobPosting).filter(JobPosting.id == candidate.job_posting_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Admin who created the job
    admin_user = db.query(User).filter(User.email == job.created_by).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Job creator admin not found")

    # Notification to admin
    notification = Notification(
        candidate_id=candidate.id,
        user_id=admin_user.id,
        message=f"New candidate {candidate.first_name} {candidate.last_name} applied for job '{job.job_description.title}'."
    )
    db.add(notification)
    db.commit()

    return candidate


# -------------------------------------
# Get all candidates
# -------------------------------------

@router.get("/", response_model=List[CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()


# -------------------------------------
# Get candidate by ID
# -------------------------------------

@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
# -------------------------------------
# Update candidate
# -------------------------------------
@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    first_name: str = Form(None),
    last_name: str = Form(None),
    interview_datetime: datetime = Form(None),
    status: str = Form(None),
    resume: UploadFile = File(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if first_name:
        candidate.first_name = first_name
    if last_name:
        candidate.last_name = last_name
    if interview_datetime:
        candidate.interview_datetime = interview_datetime
    if status:
        candidate.status = status
    if resume:
        candidate.resume_url = upload_file_to_s3(resume, folder="candidate_resumes")

    db.commit()
    db.refresh(candidate)

    return candidate
# ---------------------------------------------------------
# Update candidate status and send email if accepted
#------------------------------------------------------------
from app.permission_dependencies import require_edit_permission

@router.put(
    "/{candidate_id}/status/{new_status}",
    response_model=CandidateResponse,
    dependencies=[Depends(require_edit_permission)]   # ⬅️ Only admins/editors can access
)
async def update_candidate_status(
    candidate_id: int,
    new_status: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if new_status not in ["Accepted", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = new_status
    db.commit()
    db.refresh(candidate)

    # ────────────────────────────────
    # SEND EMAIL WHEN ACCEPTED
    # ────────────────────────────────
    if new_status == "Accepted":
        job_posting = candidate.job_posting
        job_title = job_posting.job_description.title

        html_body = render_email(
            "accepted_email.html",
            {
                "candidate_name": f"{candidate.first_name} {candidate.last_name}",
                "job_title": job_title,
                "location": job_posting.location,
                "interview_datetime": None,
                "organization_name": "Your organization Name",
                "organization_logo": None,
            },
        )
        background_tasks.add_task(
            send_email_ses,
            subject=f"Your Application for {job_title} is Accepted",
            body=html_body,
            to_email=candidate.email
        )

    # ────────────────────────────────
    # SEND EMAIL WHEN REJECTED
    # ────────────────────────────────
    if new_status == "Rejected":
        job_posting = candidate.job_posting
        job_title = job_posting.job_description.title

        html_body = render_email(
            "rejected_email.html",
            {
                "candidate_name": f"{candidate.first_name} {candidate.last_name}",
                "job_title": job_title,
                "organization_name": "Your organization Name",
                "organization_logo": None,
            },
        )

        background_tasks.add_task(
            send_email_ses,
            subject=f"Update on Your Application for {job_title}",
            body=html_body,
            to_email=candidate.email
        )

    return candidate
