from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint,String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class RoleRight(Base):
    __tablename__ = "role_rights"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    
    can_view = Column(Boolean, default=False)
    can_create = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="role_rights")
    menu = relationship("Menu", back_populates="role_rights")

    # Ensure unique constraint: one role can have only one entry per menu
    __table_args__ = (
        UniqueConstraint('role_id', 'menu_id', name='unique_role_menu'),
    )
