from sqlalchemy import Column, Integer, String, Numeric, Boolean,func,DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class AddOn(Base):
    __tablename__ = "add_ons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)#extra storage,extra users etc
    description = Column(String(255), nullable=True)
    addon_type=Column(String(50), nullable=False)  # e.g., "extra_storage", "priority_support",users,branches,features
    price = Column(Numeric(10, 2), nullable=False)
    unit=Column(String(50), nullable=True)  # e.g., "MB", "per user", "per months"
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationships
    organization_add_ons = relationship("OrganizationAddOn",back_populates="add_on")