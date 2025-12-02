from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    role_id: int
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    department_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None

    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = False
    biometric_id: Optional[str] = None
    shift_roster_id: Optional[int] = None

# User creation: no relieving_date
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# Update user: can update relieving_date (when leaving)
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    department_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None  # only for resignation/exit

    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = None
    biometric_id: Optional[str] = None
    shift_roster_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    relieving_date: Optional[date] = None  # can appear in response

    model_config = {
        "from_attributes": True
    }

#------------------------
# Authentication Schemas
#------------------------

class AuthRegister(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    role_id: Optional[int] = None


class AuthRegisterResponse(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    role_id: Optional[int] = None
    
    class Config:
        from_attributes = True