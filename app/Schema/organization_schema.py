from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    organization_logo: Optional[str] = None  # lowercase to match model

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    organization_logo: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


# app/schema/organization_schema.py

from pydantic import BaseModel
from typing import Optional

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: int
    organization_logo: Optional[str]

    
    model_config = {
        "from_attributes": True  # was orm_mode in v1
    }

