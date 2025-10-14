from pydantic import BaseModel, HttpUrl
from typing import Optional

class CandidateDocumentBase(BaseModel):
    document_type: str

class CandidateDocumentCreate(CandidateDocumentBase):
    document_url: HttpUrl

class CandidateDocumentResponse(CandidateDocumentBase):
    id: int
    document_url: HttpUrl
    candidate_id: int

    class Config:
        from_attributes = True
