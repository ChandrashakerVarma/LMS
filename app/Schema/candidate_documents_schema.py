from pydantic import BaseModel, HttpUrl
from typing import Optional

class CandidateDocumentBase(BaseModel):
    candidate_id: int
    document_type: str
    document_url: HttpUrl

class CandidateDocumentCreate(CandidateDocumentBase):
    pass

class CandidateDocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_url: Optional[HttpUrl] = None

class CandidateDocumentResponse(CandidateDocumentBase):
    id: int

    class Config:
        orm_mode = True
