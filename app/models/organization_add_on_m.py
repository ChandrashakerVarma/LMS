from sqlalchemy import Column, Integer, String,DateTime,func,Boolean,Numeric,ForeignKey,Date
from sqlalchemy.orm import relationship
from app.database import Base

class OrganizationAddOn(Base):
    __tablename__="organization_add_ons"
    
    id = Column(Integer,primary_key=True,index=True)
    organization_id = Column(Integer,ForeignKey("organizations.id",ondelete="CASCADE"))
    addon_id = Column(Integer,ForeignKey("add_ons.id"))
    
    quantity = Column(Integer,default=1) #ex 5 extra users
    price_paid = Column(Numeric(10,2),nullable=False)
    
    purchase_date = Column(Date,nullable=False)
    expiry_date = Column(Date,nullable=True)
    
    created_at = Column(DateTime,server_default=func.now())
    updated_at = Column(DateTime,server_default=func.now(),server_onupdate=func.now())
    
    created_by = Column(String(100),nullable=True)
    modified_by = Column(String(100),nullable=True)
    
    #Relationships
    organization = relationship("Organization",back_populates="add_ons")
    add_on = relationship("AddOn",back_populates="organization_add_ons")
    
        
        