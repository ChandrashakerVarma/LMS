from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.candidate_m import Candidate
from app.schema.candidate_schema import CandidateCreate, CandidateOut, CandidateUpdate

router = APIRouter(prefix="/candidates", tags=["Candidates"])

# ➕ Create Candidate
@router.post("/", response_model=CandidateOut)
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    db_candidate = Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return CandidateOut.from_orm(db_candidate)   # ✅ FIXED


# 📜 Get All Candidates
@router.get("/", response_model=List[CandidateOut])
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    return [CandidateOut.from_orm(c) for c in candidates]   # ✅ FIXED


# 🔍 Get Candidate by ID
@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateOut.from_orm(candidate)   # ✅ FIXED


# ✏️ Update Candidate
@router.put("/{candidate_id}", response_model=CandidateOut)
def update_candidate(candidate_id: int, updated_data: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(candidate, key, value)

    db.commit()
    db.refresh(candidate)
    return CandidateOut.from_orm(candidate)   # ✅ FIXED


# ❌ Delete Candidate
@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully"}


