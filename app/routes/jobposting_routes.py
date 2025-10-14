from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.jobposting_m import JobPosting
from app.schema.jobposting_schema import JobPostingCreate, JobPostingOut

router = APIRouter(prefix="/job_postings", tags=["Job Postings"])


# CREATE
@router.post("/", response_model=JobPostingOut)
def create_job_posting(posting: JobPostingCreate, db: Session = Depends(get_db)):
    new_posting = JobPosting(
        role_id=posting.role_id,
        description_id=posting.description_id,
        created_by_id=posting.created_by_id,
        number_of_positions=posting.number_of_positions,
        employment_type=posting.employment_type,
        location=posting.location,
        salary=posting.salary,
        posting_date=posting.posting_date,
        closing_date=posting.closing_date
    )
    db.add(new_posting)
    db.commit()
    db.refresh(new_posting)
    return new_posting


# READ SINGLE
@router.get("/{posting_id}", response_model=JobPostingOut)
def get_job_posting(posting_id: int, db: Session = Depends(get_db)):
    posting = db.query(JobPosting).filter(JobPosting.id == posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return posting


# READ ALL
@router.get("/", response_model=list[JobPostingOut])
def list_job_postings(db: Session = Depends(get_db)):
    postings = db.query(JobPosting).all()
    return postings


# UPDATE
@router.put("/{posting_id}", response_model=JobPostingOut)
def update_job_posting(posting_id: int, updated_posting: JobPostingCreate, db: Session = Depends(get_db)):
    posting = db.query(JobPosting).filter(JobPosting.id == posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    posting.role_id = updated_posting.role_id
    posting.description_id = updated_posting.description_id
    posting.created_by_id = updated_posting.created_by_id
    posting.number_of_positions = updated_posting.number_of_positions
    posting.employment_type = updated_posting.employment_type
    posting.location = updated_posting.location
    posting.salary = updated_posting.salary
    posting.posting_date = updated_posting.posting_date
    posting.closing_date = updated_posting.closing_date

    db.commit()
    db.refresh(posting)
    return posting


# DELETE
@router.delete("/{posting_id}", response_model=dict)
def delete_job_posting(posting_id: int, db: Session = Depends(get_db)):
    posting = db.query(JobPosting).filter(JobPosting.id == posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    db.delete(posting)
    db.commit()
    return {"detail": f"Job posting {posting_id} deleted successfully"}
