from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


# ==========================================================
# 🔹 BASE SCHEMA
# ==========================================================

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

    # ✅ NEW FIELD
    shift_roster_id: Optional[int] = None


# ==========================================================
# 🔹 CREATE SCHEMA
# ==========================================================

class UserCreate(UserBase):
    password: str


# ==========================================================
# 🔹 UPDATE SCHEMA
# ==========================================================

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

    # ✅ NEW FIELD (allow update)
    shift_roster_id: Optional[int] = None


# ==========================================================
# 🔹 RESPONSE SCHEMA
# ==========================================================

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    # 🔹 Additional fields for UI
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    organization_name: Optional[str] = None

    # 🔹 NEW: Return selected shift roster name
    shift_roster_name: Optional[str] = None

    class Config:
        from_attributes = True  # (orm_mode replacement)


# ==========================================================
# 🔹 AUTH SCHEMAS
# ==========================================================

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
