from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.jobrole_m import JobRole
from app.schema.jobrole_schema import JobRoleCreate, JobRoleOut, JobRoleUpdate
from typing import List

router = APIRouter(
    prefix="/job-roles",
    tags=["Job Roles"]
)

# Create Job Role
@router.post("/", response_model=JobRoleOut)
def create_job_role(role: JobRoleCreate, db: Session = Depends(get_db)):
    new_role = JobRole(**role.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

# Get all Job Roles
@router.get("/", response_model=List[JobRoleOut])
def get_all_job_roles(db: Session = Depends(get_db)):
    roles = db.query(JobRole).all()
    return roles

# Get Job Role by ID
@router.get("/{role_id}", response_model=JobRoleOut)
def get_job_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Job role not found")
    return role

# Update Job Role
@router.put("/{role_id}", response_model=JobRoleOut)
def update_job_role(role_id: int, role: JobRoleUpdate, db: Session = Depends(get_db)):
    db_role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Job role not found")

    for key, value in role.dict().items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role

# Delete Job Role
@router.delete("/{role_id}")
def delete_job_role(role_id: int, db: Session = Depends(get_db)):
    db_role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Job role not found")

    db.delete(db_role)
    db.commit()
    return {"detail": "Job role deleted successfully"}
