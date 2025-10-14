from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.jobrole_m import JobRole
from app.schema.jobrole_schema import JobRoleCreate, JobRoleUpdate, JobRoleOut

router = APIRouter(prefix="/roles", tags=["Job Roles"])

# 🟢 Create Role (Admin only)
@router.post("/", response_model=JobRoleOut)
def create_role(role: JobRoleCreate, db: Session = Depends(get_db)):
    existing_role = db.query(JobRole).filter(JobRole.role_name == role.role_name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role name already exists")

    new_role = JobRole(
        role_name=role.role_name,
        description=role.description,
        required_skills=role.required_skills
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

# 🔵 Read One Role (Admin/User)
@router.get("/{role_id}", response_model=JobRoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

# 🟣 Read All Roles (Admin/User)
@router.get("/", response_model=List[JobRoleOut])
def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(JobRole).all()
    return roles

# 🟠 Update Role (Admin only)
@router.put("/{role_id}", response_model=JobRoleOut)
def update_role(role_id: int, updated_role: JobRoleUpdate, db: Session = Depends(get_db)):
    role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.role_name = updated_role.role_name
    role.description = updated_role.description
    role.required_skills = updated_role.required_skills

    db.commit()
    db.refresh(role)
    return role

# 🔴 Delete Role (Admin only)
@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()
    return {"message": f"Role ID {role_id} deleted successfully"}
