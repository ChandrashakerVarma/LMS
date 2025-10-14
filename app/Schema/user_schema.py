from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

# ---------------------- Base Schema ----------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    date_of_birth: Optional[date] = None         # Only date, not datetime
    joining_date: Optional[datetime] = None      # Full datetime
    relieving_date: Optional[datetime] = None    # Optional datetime, can be null


# ---------------------- Create Schema ----------------------
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)    # Ensure password >= 6 chars


# ---------------------- Update Schema ----------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = None
    date_of_birth: Optional[date] = None
    joining_date: Optional[datetime] = None
    relieving_date: Optional[datetime] = None


# ---------------------- Response Schema ----------------------
class UserResponse(UserBase):
    id: int
    inactive: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Related names (IDs or names)
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    organization_name: Optional[str] = None

    class Config:
        orm_mode = True


# ==========================================================
# 🔹 AUTH SCHEMAS (for register & login)
# ==========================================================

class AuthRegister(BaseModel):
    """Used in /auth/register"""
    name: str
    email: EmailStr
    role_id: Optional[int] = None
    password: str = Field(..., min_length=6)


class AuthRegisterResponse(BaseModel):
    """Response for /auth/register"""
    name: str
    email: EmailStr
    role_id: Optional[int] = None

    class Config:
        orm_mode = True
