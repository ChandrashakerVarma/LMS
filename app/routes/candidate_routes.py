from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.candidate_m import Candidate
from app.schema.candidate_schema import CandidateCreate, CandidateOut, CandidateUpdate
from app.dependencies import get_current_user   #

router = APIRouter(prefix="/candidates", tags=["Candidates"])


# -------------------------
# ➕ CREATE CANDIDATE
# -------------------------
@router.post("/", response_model=CandidateOut)
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    data = candidate.model_dump()
    data["created_by"] = current_user.username   

    db_candidate = Candidate(**data)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    return CandidateOut.from_orm(db_candidate)


# -------------------------
# 📜 GET ALL CANDIDATES
# -------------------------
@router.get("/", response_model=List[CandidateOut])
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    return [CandidateOut.from_orm(c) for c in candidates]


# -------------------------
# 🔍 GET CANDIDATE BY ID
# -------------------------
@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return CandidateOut.from_orm(candidate)


# -------------------------
# ✏️ UPDATE CANDIDATE
# -------------------------
@router.put("/{candidate_id}", response_model=CandidateOut)
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

    db.commit()
    db.refresh(candidate)

    return CandidateOut.from_orm(candidate)


# -------------------------
# ❌ DELETE CANDIDATE
# -------------------------
@router.delete("/{candidate_id}")
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
