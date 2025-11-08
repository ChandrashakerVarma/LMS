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
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # replaces orm_mode in Pydantic v2
    }
