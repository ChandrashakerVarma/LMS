from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: EmailStr
    role_id: int
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    department_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None

    address: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    inactive: Optional[bool] = False
    biometric_id: Optional[str] = Field(None, max_length=50)
    shift_roster_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema for creating a new user within an organization"""
    password: str = Field(..., min_length=6)
    # organization_id is now required (will be set from current user's org)
    # branch_id is optional but recommended


class UserUpdate(BaseModel):
    """Schema for updating user details"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None

    address: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    inactive: Optional[bool] = None
    biometric_id: Optional[str] = Field(None, max_length=50)
    shift_roster_id: Optional[int] = None


class UserResponse(UserBase):
    """Standard user response"""
    id: int
    is_org_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserDetailResponse(UserResponse):
    """Detailed user response with relationship data"""
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    organization_name: Optional[str] = None
    department_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


# ============================================
# Auth Schemas
# ============================================

class AuthRegister(BaseModel):
    """Registration schema - creates user + organization"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    # Organization details (optional - will auto-create if not provided)
    organization_name: Optional[str] = Field(None, max_length=150)
    contact_phone: Optional[str] = Field(None, max_length=20)


class AuthRegisterResponse(BaseModel):
    """Response after successful registration"""
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    
    # Organization info
    organization_id: int
    organization_name: str
    is_org_admin: bool
    
    # Subscription info
    subscription_status: str
    subscription_end_date: Optional[date] = None
    trial_days_remaining: Optional[int] = None
    
    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Response after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: dict