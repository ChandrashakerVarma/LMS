from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    role_id: int
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = False
    biometric_id: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = None
    biometric_id: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

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
