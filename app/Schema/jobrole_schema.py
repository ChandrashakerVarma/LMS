from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobRoleBase(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: Optional[str] = None

class JobRoleCreate(JobRoleBase):
    pass

class JobRoleUpdate(JobRoleBase):
    pass

class JobRoleOut(JobRoleBase):
    id: int
    created_at: Optional[datetime] = None  # <-- make optional
    updated_at: Optional[datetime] = None
    created_by: str | None = None
    modified_by: str | None = None

    class Config:
        orm_mode = True  # Required for from_orm()
