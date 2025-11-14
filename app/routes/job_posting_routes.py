from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job_posting_m import JobPosting
from app.schema.job_posting_schema import JobPostingCreate, JobPostingOut
from app.dependencies import get_current_user
from app.models.user_m import User

router = APIRouter(prefix="/job_postings", tags=["Job Postings"])


# ---------------- CREATE JOB POSTING ----------------
@router.post("/", response_model=JobPostingOut)
def create_job_posting(
    job_posting: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ inject authenticated user
):
    """
    Create a new job posting. `created_by_id` will be set to the current user.
    """
    new_posting = JobPosting(
        **job_posting.dict(),
        created_by_id=current_user.id  # ✅ must be real user ID
    )
    db.add(new_posting)
    db.commit()
    db.refresh(new_posting)
    return new_posting


# ---------------- GET ALL JOB POSTINGS ----------------
@router.get("/", response_model=list[JobPostingOut])
def get_all_job_postings(db: Session = Depends(get_db)):
    postings = db.query(JobPosting).all()
    return postings


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
    job_posting: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Optional: only creator can update
    if posting.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this posting")

    for key, value in job_posting.dict().items():
        setattr(posting, key, value)

    db.commit()
    db.refresh(posting)
    return posting


# ---------------- DELETE JOB POSTING ----------------
@router.delete("/{job_posting_id}")
def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Optional: only creator can delete
    if posting.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this posting")

    db.delete(posting)
    db.commit()
    return {"detail": "Job posting deleted successfully"}
