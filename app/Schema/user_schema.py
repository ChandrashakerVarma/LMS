from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date, datetime

# ---------------------------------------------------------
# Base User Fields
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Create User (includes password + auto username)
# ---------------------------------------------------------
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    username: Optional[str] = None

    @field_validator("username", mode="before")
    def auto_generate_username(cls, v, values):
        if v:
            return v.lower().replace(" ", "")

        first = values.get("first_name", "")
        last = values.get("last_name", "")

        username = (first + last).lower().replace(" ", "")
        return username


# ---------------------------------------------------------
# Update User
# ---------------------------------------------------------
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    department_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None

    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = None
    biometric_id: Optional[str] = None
    shift_roster_id: Optional[int] = None


# ---------------------------------------------------------
# Response Model
# ---------------------------------------------------------
class UserResponse(UserBase):
    id: int
    username: str
    created_at: datetime
    updated_at: datetime
    relieving_date: Optional[date] = None

    model_config = {
        "from_attributes": True
    }


# ---------------------------------------------------------
# Authentication Schemas
# ---------------------------------------------------------
class AuthRegister(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    role_id: Optional[int] = None
    username: Optional[str] = None

    @field_validator("username", mode="before")
    def auto_username(cls, v, values):
        if v:
            return v.lower().replace(" ", "")

        first = values.get("first_name", "")
        last = values.get("last_name", "")
        return (first + last).lower().replace(" ", "")


class AuthRegisterResponse(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    role_id: Optional[int] = None
    username: str

    model_config = {
        "from_attributes": True
    }

