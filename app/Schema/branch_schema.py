# app/schema/branch_schema.py
from pydantic import BaseModel
from typing import Optional

class BranchBase(BaseModel):
    name: str
    address: Optional[str] = None
    organization_id: int

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    organization_id: Optional[int]

class BranchResponse(BranchBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True
