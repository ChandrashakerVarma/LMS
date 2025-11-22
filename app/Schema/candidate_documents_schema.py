from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class CandidateDocumentBase(BaseModel):
    candidate_id: int
    document_type: str
    document_url: HttpUrl

class CandidateDocumentCreate(CandidateDocumentBase):
    pass

class CandidateDocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_url: Optional[HttpUrl] = None

class CandidateDocumentOut(BaseModel):
    id: int
    candidate_id: int
    document_type: str
    document_url: HttpUrl
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    modified_by: str | None = None


    model_config = {"from_attributes": True}
