from pydantic import BaseModel
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

    class Config:
        from_attributes = True
